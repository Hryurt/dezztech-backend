import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.exceptions import UserAlreadyExistsException, UserNotFoundException
from src.users.models import User


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
    """Get a user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object

    Raises:
        UserNotFoundException: If user not found
    """
    user = await db.get(User, user_id)
    if not user:
        raise UserNotFoundException(user_id=user_id)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get a user by email.

    Args:
        db: Database session
        email: User email

    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    return user


async def create_user(
    db: AsyncSession,
    email: str,
    hashed_password: str,
    full_name: str,
    is_active: bool = True,
    is_superuser: bool = False,
) -> User:
    """Create a new user.

    Args:
        db: Database session
        email: User email
        hashed_password: Hashed password
        full_name: User full name
        is_active: User active status (default: True)
        is_superuser: User superuser status (default: False)

    Returns:
        Created user object

    Raises:
        UserAlreadyExistsException: If user with email already exists
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, email)
    if existing_user:
        raise UserAlreadyExistsException(email=email)

    # Create new user
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=is_active,
        is_superuser=is_superuser,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user
