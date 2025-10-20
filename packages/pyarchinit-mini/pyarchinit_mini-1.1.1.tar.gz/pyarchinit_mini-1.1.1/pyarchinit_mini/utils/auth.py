"""
Authentication utilities for JWT and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

try:
    from passlib.context import CryptContext
    from jose import JWTError, jwt
    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False


# Password hashing context
if PASSLIB_AVAILABLE:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthUtils:
    """Authentication utility functions"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            bool: True if password matches
        """
        if not PASSLIB_AVAILABLE:
            raise ImportError(
                "passlib is required for password hashing. "
                "Install with: pip install 'passlib[bcrypt]'"
            )
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        if not PASSLIB_AVAILABLE:
            raise ImportError(
                "passlib is required for password hashing. "
                "Install with: pip install 'passlib[bcrypt]'"
            )
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            str: JWT token
        """
        if not PASSLIB_AVAILABLE:
            raise ImportError(
                "python-jose is required for JWT tokens. "
                "Install with: pip install 'python-jose[cryptography]'"
            )

        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode a JWT access token

        Args:
            token: JWT token

        Returns:
            Dict or None: Decoded payload or None if invalid
        """
        if not PASSLIB_AVAILABLE:
            raise ImportError(
                "python-jose is required for JWT tokens. "
                "Install with: pip install 'python-jose[cryptography]'"
            )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None


# Convenience functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password (convenience function)"""
    return AuthUtils.verify_password(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash password (convenience function)"""
    return AuthUtils.hash_password(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token (convenience function)"""
    return AuthUtils.create_access_token(data, expires_delta)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode access token (convenience function)"""
    return AuthUtils.decode_access_token(token)
