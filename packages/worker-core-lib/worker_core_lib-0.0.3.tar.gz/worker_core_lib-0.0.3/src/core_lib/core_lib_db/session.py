from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..core_lib_config.settings import DBSettings

def get_db_session(db_settings: DBSettings) -> Session:
    """
    Creates a new database session.

    Args:
        db_settings: The database connection settings.

    Returns:
        A new SQLAlchemy Session object.
    """
    print("Creating database session...")
    engine = create_engine(db_settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()