"""
Authentication API endpoints
"""

from typing import Optional
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.user_service import UserService
from pyarchinit_mini.models.user import UserRole
from pyarchinit_mini.utils.auth import create_access_token, decode_access_token
from pyarchinit_mini.api.dependencies import get_db_manager


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic schemas
class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_superuser: bool


class UserCreate(BaseModel):
    """User creation schema"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


# Router
router = APIRouter(prefix="/api/auth", tags=["authentication"])


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_manager: DatabaseManager = Depends(get_db_manager)
) -> dict:
    """
    Get current authenticated user from token

    Args:
        token: JWT token
        db_manager: Database manager

    Returns:
        dict: Current user data

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Get user
    user_service = UserService(db_manager)
    user = user_service.get_user_by_username(username)

    if user is None:
        raise credentials_exception

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    return user


async def get_current_active_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verify current user is admin

    Args:
        current_user: Current user from token

    Returns:
        dict: Current user data

    Raises:
        HTTPException: If user is not admin
    """
    if current_user["role"] != UserRole.ADMIN.value and not current_user["is_superuser"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return current_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Login endpoint - Returns JWT token

    Args:
        form_data: Username and password
        db_manager: Database manager

    Returns:
        Token: Access token
    """
    user_service = UserService(db_manager)
    user = user_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse: Current user data
    """
    return current_user


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db_manager: DatabaseManager = Depends(get_db_manager),
    current_user: dict = Depends(get_current_active_admin)
):
    """
    Register a new user (admin only)

    Args:
        user_data: User creation data
        db_manager: Database manager
        current_user: Current admin user

    Returns:
        UserResponse: Created user
    """
    user_service = UserService(db_manager)

    try:
        user = user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db_manager: DatabaseManager = Depends(get_db_manager),
    current_user: dict = Depends(get_current_active_admin)
):
    """
    List all users (admin only)

    Args:
        db_manager: Database manager
        current_user: Current admin user

    Returns:
        List[UserResponse]: List of all users
    """
    user_service = UserService(db_manager)
    users = user_service.get_all_users()
    return users


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db_manager: DatabaseManager = Depends(get_db_manager),
    current_user: dict = Depends(get_current_active_admin)
):
    """
    Update user (admin only)

    Args:
        user_id: User ID to update
        user_data: Update data
        db_manager: Database manager
        current_user: Current admin user

    Returns:
        UserResponse: Updated user
    """
    user_service = UserService(db_manager)

    # Prepare update dict (exclude None values)
    updates = {k: v for k, v in user_data.dict().items() if v is not None}

    user = user_service.update_user(user_id, **updates)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db_manager: DatabaseManager = Depends(get_db_manager),
    current_user: dict = Depends(get_current_active_admin)
):
    """
    Delete user (admin only)

    Args:
        user_id: User ID to delete
        db_manager: Database manager
        current_user: Current admin user

    Returns:
        dict: Success message
    """
    # Prevent deleting yourself
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user_service = UserService(db_manager)
    deleted = user_service.delete_user(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User deleted successfully"}
