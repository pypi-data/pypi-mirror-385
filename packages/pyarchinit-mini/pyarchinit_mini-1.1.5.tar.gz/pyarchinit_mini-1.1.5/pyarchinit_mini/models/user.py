"""
User model for authentication and authorization
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"           # Full access to everything
    OPERATOR = "operator"     # Can create/edit/delete data
    VIEWER = "viewer"         # Read-only access


class User(BaseModel):
    """User model for authentication"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission

        Args:
            permission: Permission name (e.g., 'create', 'edit', 'delete')

        Returns:
            bool: True if user has permission
        """
        if self.is_superuser:
            return True

        # Permission mapping by role
        permissions = {
            UserRole.ADMIN: ['create', 'read', 'update', 'delete', 'manage_users'],
            UserRole.OPERATOR: ['create', 'read', 'update', 'delete'],
            UserRole.VIEWER: ['read']
        }

        return permission in permissions.get(self.role, [])

    def can_create(self) -> bool:
        """Check if user can create records"""
        return self.has_permission('create')

    def can_edit(self) -> bool:
        """Check if user can edit records"""
        return self.has_permission('update')

    def can_delete(self) -> bool:
        """Check if user can delete records"""
        return self.has_permission('delete')

    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.has_permission('manage_users')
