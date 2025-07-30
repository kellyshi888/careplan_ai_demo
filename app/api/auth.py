from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..models.auth import (
    LoginRequest, LoginResponse, RegisterRequest, 
    PasswordChangeRequest, User
)
from ..auth.service import AuthenticationService
from ..logging.audit import audit_log

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

# Global auth service instance (in production, use dependency injection)
auth_service = AuthenticationService()


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Extract user agent from request"""
    return request.headers.get("User-Agent", "unknown")


@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Patient login endpoint"""
    try:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        login_response = await auth_service.login(
            login_request=login_request,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not login_response:
            # Log failed login attempt
            background_tasks.add_task(
                audit_log,
                action="login_failed",
                details={
                    "email": login_request.email,
                    "ip_address": ip_address,
                    "user_agent": user_agent
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Log successful login
        background_tasks.add_task(
            audit_log,
            action="login_success",
            user_id=login_response.user["user_id"],
            details={
                "email": login_request.email,
                "ip_address": ip_address,
                "session_id": login_response.session_id
            }
        )
        
        return login_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )


@router.post("/logout")
async def logout(
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Patient logout endpoint"""
    try:
        # Validate current session
        user_session = await auth_service.validate_session(credentials.credentials)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user, session = user_session
        
        # Logout user
        success = await auth_service.logout(
            session_id=session.session_id,
            user_id=user.user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
        
        # Log logout
        background_tasks.add_task(
            audit_log,
            action="logout",
            user_id=user.user_id,
            details={"session_id": session.session_id}
        )
        
        return {"message": "Successfully logged out"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed due to server error"
        )


@router.post("/logout-all")
async def logout_all_sessions(
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout from all sessions"""
    try:
        # Validate current session
        user_session = await auth_service.validate_session(credentials.credentials)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user, _ = user_session
        
        # Logout from all sessions
        sessions_count = await auth_service.logout_all_sessions(user.user_id)
        
        # Log logout all
        background_tasks.add_task(
            audit_log,
            action="logout_all_sessions",
            user_id=user.user_id,
            details={"sessions_terminated": sessions_count}
        )
        
        return {
            "message": f"Successfully logged out from {sessions_count} sessions"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout all failed due to server error"
        )


@router.post("/register")
async def register(
    register_request: RegisterRequest,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Patient registration endpoint"""
    try:
        ip_address = get_client_ip(request)
        
        # Register user
        user = await auth_service.register_user(register_request)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. Email may already be in use or passwords don't match."
            )
        
        # Log registration
        background_tasks.add_task(
            audit_log,
            action="user_registered",
            user_id=user.user_id,
            details={
                "email": register_request.email,
                "ip_address": ip_address,
                "role": user.role.value
            }
        )
        
        return {
            "message": "Registration successful. Please verify your email to activate your account.",
            "user_id": user.user_id,
            "email": user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )


@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current user profile"""
    try:
        # Validate session
        user_session = await auth_service.validate_session(credentials.credentials)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user, session = user_session
        
        # Return user profile (exclude sensitive info)
        return {
            "user_id": user.user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "patient_id": user.patient_id,
            "phone_number": user.phone_number,
            "email_verified": user.email_verified,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "session_expires_at": session.expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.put("/profile")
async def update_profile(
    profile_updates: dict,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update user profile"""
    try:
        # Validate session
        user_session = await auth_service.validate_session(credentials.credentials)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user, _ = user_session
        
        # Update profile
        updated_user = await auth_service.update_user_profile(
            user_id=user.user_id,
            updates=profile_updates
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile update failed"
            )
        
        # Log profile update
        background_tasks.add_task(
            audit_log,
            action="profile_updated",
            user_id=user.user_id,
            details={"updated_fields": list(profile_updates.keys())}
        )
        
        return {"message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed due to server error"
        )


@router.post("/change-password")
async def change_password(
    password_change: PasswordChangeRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Change user password"""
    try:
        # Validate password confirmation
        if password_change.new_password != password_change.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords don't match"
            )
        
        # Validate session
        user_session = await auth_service.validate_session(credentials.credentials)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user, _ = user_session
        
        # Change password
        success = await auth_service.change_password(
            user_id=user.user_id,
            current_password=password_change.current_password,
            new_password=password_change.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password change failed. Current password is incorrect."
            )
        
        # Log password change
        background_tasks.add_task(
            audit_log,
            action="password_changed",
            user_id=user.user_id
        )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed due to server error"
        )


@router.get("/validate-token")
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Validate if token is still valid"""
    try:
        user_session = await auth_service.validate_session(credentials.credentials)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user, session = user_session
        
        return {
            "valid": True,
            "user_id": user.user_id,
            "expires_at": session.expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {"valid": False}