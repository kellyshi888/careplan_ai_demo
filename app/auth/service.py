from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import secrets
import json
from pathlib import Path

try:
    import jwt
except ImportError:
    import PyJWT as jwt

from passlib.context import CryptContext

from ..models.auth import (
    User, UserSession, LoginRequest, LoginResponse, RegisterRequest,
    UserRole, UserStatus, AuthToken, TokenPayload, SecurityEvent
)
from ..logging.audit import security_audit_log


class AuthenticationService:
    """Service for handling user authentication and session management"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or "your-secret-key-change-in-production"
        self.algorithm = "HS256"
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # In-memory storage for development (use database in production)
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, UserSession] = {}
        self._email_to_user_id: Dict[str, str] = {}
        
        # Load sample users
        self._load_sample_users()
    
    def _load_sample_users(self):
        """Load sample users for development"""
        sample_users = [
            {
                "user_id": "user_6f6f76a7-e502-474f-af36-48aca5cec7f3",
                "email": "jerry.clark@email.com",
                "password": "password123",
                "first_name": "Jerry",
                "last_name": "Clark",
                "role": UserRole.PATIENT,
                "patient_id": "6f6f76a7-e502-474f-af36-48aca5cec7f3",
                "phone_number": "+1-555-0101",
                "date_of_birth": datetime(2003, 8, 2)
            },
            {
                "user_id": "user_f8f82d73-28ff-488e-b649-625ecbe7c577",
                "email": "tina.hall@email.com", 
                "password": "password123",
                "first_name": "Tina",
                "last_name": "Hall",
                "role": UserRole.PATIENT,
                "patient_id": "f8f82d73-28ff-488e-b649-625ecbe7c577",
                "phone_number": "+1-555-0102"
            },
            {
                "user_id": "user_clinician_1",
                "email": "dr.garcia@hospital.com",
                "password": "doctor123",
                "first_name": "Maria",
                "last_name": "Garcia",
                "role": UserRole.CLINICIAN
            },
            {
                "user_id": "user_admin_1",
                "email": "admin@hospital.com",
                "password": "admin123",
                "first_name": "System",
                "last_name": "Administrator",
                "role": UserRole.ADMIN
            }
        ]
        
        for user_data in sample_users:
            password = user_data.pop("password")
            user = User(
                **user_data,
                hashed_password=self._hash_password(password),
                email_verified=True,
                status=UserStatus.ACTIVE
            )
            self._users[user.user_id] = user
            self._email_to_user_id[user.email] = user.user_id
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.password_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.password_context.verify(plain_password, hashed_password)
    
    def _generate_token(self, user: User, session: UserSession) -> str:
        """Generate JWT access token"""
        payload = {
            "user_id": user.user_id,
            "session_id": session.session_id,
            "role": user.role.value,
            "exp": session.expires_at,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _verify_token(self, token: str) -> Optional[TokenPayload]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return TokenPayload(
                user_id=payload["user_id"],
                session_id=payload["session_id"],
                role=UserRole(payload["role"]),
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"])
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    async def authenticate_user(self, email: str, password: str, ip_address: str = None) -> Optional[User]:
        """Authenticate user with email and password"""
        user_id = self._email_to_user_id.get(email)
        if not user_id:
            await security_audit_log(
                event_type="login_attempt",
                severity="warning",
                description=f"Login attempt with non-existent email: {email}",
                ip_address=ip_address
            )
            return None
        
        user = self._users.get(user_id)
        if not user:
            return None
        
        # Check if account is locked
        if user.account_locked_until and datetime.utcnow() < user.account_locked_until:
            await security_audit_log(
                event_type="login_locked_account",
                severity="warning", 
                description=f"Login attempt on locked account: {email}",
                user_id=user.user_id,
                ip_address=ip_address
            )
            return None
        
        # Verify password
        if not self._verify_password(password, user.hashed_password):
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.account_locked_until = datetime.utcnow() + timedelta(hours=1)
                await security_audit_log(
                    event_type="account_locked",
                    severity="high",
                    description=f"Account locked due to failed login attempts: {email}",
                    user_id=user.user_id,
                    ip_address=ip_address
                )
            
            await security_audit_log(
                event_type="login_failed",
                severity="warning",
                description=f"Failed login attempt for: {email}",
                user_id=user.user_id,
                ip_address=ip_address
            )
            return None
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.last_login = datetime.utcnow()
        
        await security_audit_log(
            event_type="login_success",
            severity="info",
            description=f"Successful login: {email}",
            user_id=user.user_id,
            ip_address=ip_address
        )
        
        return user
    
    async def login(self, login_request: LoginRequest, ip_address: str = None, user_agent: str = None) -> Optional[LoginResponse]:
        """Handle user login"""
        user = await self.authenticate_user(login_request.email, login_request.password, ip_address)
        if not user:
            return None
        
        # Create session
        session_duration = 30 * 24 if login_request.remember_me else 24  # 30 days vs 24 hours
        session = UserSession.create_session(
            user_id=user.user_id,
            duration_hours=session_duration,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self._sessions[session.session_id] = session
        
        # Generate access token
        access_token = self._generate_token(user, session)
        
        # Prepare user data for response (exclude sensitive info)
        user_data = {
            "user_id": user.user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "patient_id": user.patient_id,
            "phone_number": user.phone_number,
            "email_verified": user.email_verified
        }
        
        return LoginResponse(
            access_token=access_token,
            expires_in=int(session_duration * 3600),  # Convert to seconds
            user=user_data,
            session_id=session.session_id
        )
    
    async def logout(self, session_id: str, user_id: str = None) -> bool:
        """Handle user logout"""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        if user_id and session.user_id != user_id:
            return False
        
        # Deactivate session
        session.is_active = False
        
        await security_audit_log(
            event_type="logout",
            severity="info",
            description=f"User logged out",
            user_id=session.user_id
        )
        
        return True
    
    async def logout_all_sessions(self, user_id: str) -> int:
        """Logout user from all sessions"""
        count = 0
        for session in self._sessions.values():
            if session.user_id == user_id and session.is_active:
                session.is_active = False
                count += 1
        
        await security_audit_log(
            event_type="logout_all_sessions",
            severity="info",
            description=f"User logged out from all sessions",
            user_id=user_id
        )
        
        return count
    
    async def validate_session(self, token: str) -> Optional[Tuple[User, UserSession]]:
        """Validate session token and return user and session"""
        token_payload = self._verify_token(token)
        if not token_payload:
            return None
        
        session = self._sessions.get(token_payload.session_id)
        if not session or not session.is_active or session.is_expired():
            return None
        
        user = self._users.get(token_payload.user_id)
        if not user or user.status != UserStatus.ACTIVE:
            return None
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        
        return user, session
    
    async def register_user(self, register_request: RegisterRequest) -> Optional[User]:
        """Register a new patient user"""
        # Check if email already exists
        if register_request.email in self._email_to_user_id:
            return None
        
        # Validate password confirmation
        if register_request.password != register_request.confirm_password:
            return None
        
        # Create new user ID
        import uuid
        user_id = f"user_{str(uuid.uuid4())}"
        patient_id = str(uuid.uuid4())
        
        # Create user
        user = User(
            user_id=user_id,
            email=register_request.email,
            hashed_password=self._hash_password(register_request.password),
            first_name=register_request.first_name,
            last_name=register_request.last_name,
            role=UserRole.PATIENT,
            patient_id=patient_id,
            phone_number=register_request.phone_number,
            date_of_birth=register_request.date_of_birth,
            emergency_contact=register_request.emergency_contact,
            status=UserStatus.PENDING  # Email verification required
        )
        
        self._users[user_id] = user
        self._email_to_user_id[register_request.email] = user_id
        
        await security_audit_log(
            event_type="user_registered",
            severity="info",
            description=f"New user registered: {register_request.email}",
            user_id=user_id
        )
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_id = self._email_to_user_id.get(email)
        return self._users.get(user_id) if user_id else None
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user profile"""
        user = self._users.get(user_id)
        if not user:
            return None
        
        # Only allow certain fields to be updated
        allowed_fields = {
            "first_name", "last_name", "phone_number", 
            "emergency_contact", "preferences"
        }
        
        for field, value in updates.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        return user
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self._users.get(user_id)
        if not user:
            return False
        
        if not self._verify_password(current_password, user.hashed_password):
            await security_audit_log(
                event_type="password_change_failed",
                severity="warning",
                description="Failed password change attempt - wrong current password",
                user_id=user_id
            )
            return False
        
        user.hashed_password = self._hash_password(new_password)
        
        await security_audit_log(
            event_type="password_changed",
            severity="info",
            description="User password changed successfully",
            user_id=user_id
        )
        
        return True
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = []
        for session_id, session in self._sessions.items():
            if session.is_expired():
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        return len(expired_sessions)