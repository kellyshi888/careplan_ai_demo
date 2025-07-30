from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class UserRole(str, Enum):
    PATIENT = "patient"
    CLINICIAN = "clinician"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class User(BaseModel):
    user_id: str
    email: EmailStr
    hashed_password: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    patient_id: Optional[str] = None  # Links to patient data if role is PATIENT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    email_verified: bool = False
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserSession(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    
    @classmethod
    def create_session(cls, user_id: str, duration_hours: int = 24, **kwargs) -> "UserSession":
        """Create a new user session with expiration"""
        import uuid
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        return cls(
            session_id=session_id,
            user_id=user_id,
            expires_at=expires_at,
            **kwargs
        )
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def refresh(self, duration_hours: int = 24) -> None:
        """Refresh session expiration and update last activity"""
        self.expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        self.last_activity = datetime.utcnow()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: Dict[str, Any]
    session_id: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    emergency_contact: Optional[Dict[str, Any]] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class EmailVerificationRequest(BaseModel):
    email: EmailStr
    verification_code: str


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    user_id: str
    session_id: str
    role: UserRole
    exp: datetime
    iat: datetime


class SecurityEvent(BaseModel):
    event_type: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool
    details: Dict[str, Any] = Field(default_factory=dict)