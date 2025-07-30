from typing import Optional, List
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps

from ..models.auth import User, UserRole
from .service import AuthenticationService

security = HTTPBearer()


class AuthenticationMiddleware:
    """Authentication middleware for protecting routes"""
    
    def __init__(self, auth_service: AuthenticationService):
        self.auth_service = auth_service
    
    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> User:
        """Get current authenticated user"""
        user_session = await self.auth_service.validate_session(credentials.credentials)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user, _ = user_session
        return user
    
    async def get_current_active_user(
        self,
        current_user: User = Depends(lambda: None)  # Will be overridden
    ) -> User:
        """Get current active user"""
        if not current_user:
            # This dependency will be properly injected
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        if current_user.status.value != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        
        return current_user
    
    def require_roles(self, allowed_roles: List[UserRole]):
        """Dependency factory for role-based access control"""
        async def role_checker(current_user: User = Depends(lambda: None)) -> User:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return current_user
        
        return role_checker
    
    def require_patient_access(self, patient_id: str):
        """Require patient to access their own data only"""
        async def patient_access_checker(current_user: User = Depends(lambda: None)) -> User:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            
            # Patients can only access their own data
            if current_user.role == UserRole.PATIENT and current_user.patient_id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to patient data"
                )
            
            # Clinicians and admins can access any patient data
            if current_user.role not in [UserRole.PATIENT, UserRole.CLINICIAN, UserRole.ADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return current_user
        
        return patient_access_checker


# Global middleware instance (in production, use proper dependency injection)
from .service import AuthenticationService
auth_service = AuthenticationService()
auth_middleware = AuthenticationMiddleware(auth_service)


# Convenience dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    return await auth_middleware.get_current_user(credentials)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    return await auth_middleware.get_current_active_user(current_user)


def require_roles(allowed_roles: List[UserRole]):
    """Dependency for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


def require_patient_access(patient_id: str):
    """Require access to specific patient data"""
    async def patient_access_checker(current_user: User = Depends(get_current_user)) -> User:
        # Patients can only access their own data
        if current_user.role == UserRole.PATIENT and current_user.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to patient data"
            )
        
        # Clinicians and admins can access any patient data
        if current_user.role not in [UserRole.PATIENT, UserRole.CLINICIAN, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return patient_access_checker


# Role-specific dependencies
require_patient = require_roles([UserRole.PATIENT])
require_clinician = require_roles([UserRole.CLINICIAN])
require_admin = require_roles([UserRole.ADMIN])
require_clinician_or_admin = require_roles([UserRole.CLINICIAN, UserRole.ADMIN])