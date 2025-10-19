"""
Database initialization utilities
"""

from sqlalchemy.orm import Session
from ..core.database import Base, engine, SessionLocal
from ..models.user import User
from ..core.security import get_password_hash


def init_db() -> None:
    """
    Initialize database tables
    Creates all tables defined in models
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def create_superuser(
    username: str = "admin",
    email: str = "admin@example.com",
    password: str = "admin123"
) -> User:
    """
    Create a superuser account
    
    Args:
        username: Username for the superuser
        email: Email for the superuser
        password: Password for the superuser
    
    Returns:
        User: Created superuser instance
    """
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"⚠ User already exists: {existing_user.username}")
            return existing_user
        
        # Create superuser
        hashed_password = get_password_hash(password)
        superuser = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True
        )
        
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        print(f"✓ Superuser created successfully: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        
        return superuser
    
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating superuser: {e}")
        raise
    finally:
        db.close()


def reset_db() -> None:
    """
    Drop all tables and recreate them
    WARNING: This will delete all data!
    """
    print("⚠ WARNING: Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped")
    
    init_db()


if __name__ == "__main__":
    # Initialize database and create superuser
    init_db()
    create_superuser()
