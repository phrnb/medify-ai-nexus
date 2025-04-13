
import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.schemas.user import UserCreate
from app.crud.crud_user import user as crud_user

logger = logging.getLogger(__name__)

# Create initial admin user
def create_first_superuser(db: Session) -> None:
    # Check if any user exists
    user = crud_user.get_by_email(db, email="admin@example.com")
    if not user:
        user_in = UserCreate(
            email="admin@example.com",
            password="admin123",  # Will be hashed
            full_name="Initial Admin",
            is_superuser=True,
        )
        user = crud_user.create(db, obj_in=user_in)
        logger.info(f"Created initial admin user: {user.email}")

def init_db(db: Session) -> None:
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create initial data
    create_first_superuser(db)
    
    logger.info("Database initialized")
