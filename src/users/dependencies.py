from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.service import UserService


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Get UserService instance with database session.

    Args:
        db: Database session from dependency

    Returns:
        UserService instance
    """
    return UserService(db)
