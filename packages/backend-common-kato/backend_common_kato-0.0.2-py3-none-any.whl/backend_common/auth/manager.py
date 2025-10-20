# src/backend_common/auth/manager.py
"""
Authentication manager implementations.

Provides JWT-based authentication with token generation, validation,
and user management capabilities.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..exceptions import UnauthorizedError


class UserModel(BaseModel):
    """Base user model for authentication."""

    id: str
    username: str
    email: Optional[str] = None
    is_active: bool = True
    scopes: list[str] = []


class AuthManager(ABC):
    """Abstract base class for authentication managers."""

    @abstractmethod
    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[UserModel]:
        """Authenticate user with credentials."""
        raise NotImplementedError

    @abstractmethod
    async def create_access_token(
        self, user: UserModel, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token for user."""
        raise NotImplementedError

    @abstractmethod
    async def verify_token(self, token: str) -> UserModel:
        """Verify and decode JWT token."""
        raise NotImplementedError


class JWTAuthManager(AuthManager):
    """JWT-based authentication manager implementation."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ) -> None:
        """
        Initialize JWT authentication manager.

        Args:
            secret_key: Secret key for JWT encoding/decoding
            algorithm: JWT algorithm to use
            access_token_expire_minutes: Token expiration time in minutes
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return self.pwd_context.hash(password)

    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[UserModel]:
        """
        Authenticate user with username and password.

        Note: This is a basic implementation. In production, you would
        integrate with your user database/service.
        """
        # This should be implemented to check against your user database
        # For now, return None to indicate authentication failure
        return None

    async def create_access_token(
        self, user: UserModel, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token for authenticated user."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "scopes": user.scopes,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        return encoded_jwt

    async def verify_token(self, token: str) -> UserModel:
        """Verify JWT token and return user information."""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            user_id: str = payload.get("sub")
            username: str = payload.get("username")

            if user_id is None or username is None:
                raise UnauthorizedError("Invalid token payload")

            return UserModel(
                id=user_id,
                username=username,
                email=payload.get("email"),
                scopes=payload.get("scopes", []),
            )
        except JWTError as e:
            raise UnauthorizedError(f"Token validation failed: {str(e)}")

    async def create_service_token(self, service_name: str) -> str:
        """Create service-to-service authentication token."""
        expire = datetime.utcnow() + timedelta(
            hours=24
        )  # Service tokens last longer

        to_encode = {
            "sub": f"service:{service_name}",
            "service": service_name,
            "type": "service",
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def verify_service_token(self, token: str) -> str:
        """Verify service token and return service name."""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )

            if payload.get("type") != "service":
                raise UnauthorizedError("Invalid service token")

            service_name = payload.get("service")
            if not service_name:
                raise UnauthorizedError("Missing service name in token")

            return service_name
        except JWTError as e:
            raise UnauthorizedError(
                f"Service token validation failed: {str(e)}"
            )
