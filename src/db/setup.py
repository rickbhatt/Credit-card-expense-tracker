import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from .models import Base
from app_logging.config import setup_logger, get_ui


load_dotenv()


def setup_database_tables():
    """
    Creates all database tables based on SQLAlchemy models.
    Similar to Django's migrate command.
    """
    logger = setup_logger("db_setup")
    ui = get_ui()
    
    logger.info("Starting database table setup")
    ui.process_start("Setting up database tables")
    
    try:
        # Get database connection details from environment
        db_name = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        password = os.getenv("DB_PASSWORD")
        
        if not all([db_name, user, host, port, password]):
            missing = [var for var, val in {
                "DB_NAME": db_name,
                "DB_USER": user, 
                "DB_HOST": host,
                "DB_PORT": port,
                "DB_PASSWORD": password
            }.items() if not val]
            
            error_msg = f"Missing environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            ui.error(error_msg, "Configuration Error")
            return False
        
        # Create database connection
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        logger.debug(f"Connecting to database for setup: postgresql://{user}:***@{host}:{port}/{db_name}")
        
        engine = create_engine(db_url, echo=False)
        
        # Create all tables
        logger.info("Creating database tables if they don't exist")
        Base.metadata.create_all(engine)
        
        logger.info("Database tables setup completed successfully")
        ui.success("Database tables created successfully!", "Setup Complete")
        
        # Cleanup
        engine.dispose()
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during setup: {e}")
        ui.error(f"Database error: {str(e)}", "Setup Failed")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during setup: {e}")
        ui.error(f"Setup failed: {str(e)}", "Setup Failed")
        return False


if __name__ == "__main__":
    setup_database_tables()