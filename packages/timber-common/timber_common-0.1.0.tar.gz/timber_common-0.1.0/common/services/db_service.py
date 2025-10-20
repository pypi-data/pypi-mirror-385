"""
Database Service with Connection Retry Logic for Timber Common

Features:
- Automatic retry on connection failures with exponential backoff
- SQLAlchemy session management with context managers
- Connection validation and health checks
- Connection pooling with configurable parameters
- Thread-safe singleton pattern
"""

import time
import logging
from typing import Optional, Generator, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.exc import OperationalError, DBAPIError
from sqlalchemy.pool import QueuePool

from common.utils.config import config

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class DBService:
    """
    Singleton service for managing SQLAlchemy engine and sessions with retry logic.
    """
    _instance: Optional['DBService'] = None
    _engine = None
    _SessionLocal = None
    _max_retries = 5
    _retry_delay = 2  # seconds

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBService, cls).__new__(cls)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self, max_retries: int = 5, delay: int = 5):
        """
        Initializes the SQLAlchemy engine with connection pooling and retries.
        
        Args:
            max_retries: Maximum number of connection attempts
            delay: Delay between retries in seconds
        """
        db_url = config.get_db_url()
        pool_config = config.get_pool_config()
        
        logger.info(f"Attempting to initialize DB engine to {config.DB_HOST}:{config.DB_PORT}...")

        for attempt in range(max_retries):
            try:
                # Create engine with connection pooling
                self._engine = create_engine(
                    db_url,
                    echo=config.DATABASE_ECHO,
                    poolclass=QueuePool,
                    pool_size=pool_config['pool_size'],
                    max_overflow=pool_config['max_overflow'],
                    pool_timeout=pool_config['pool_timeout'],
                    pool_recycle=pool_config['pool_recycle'],
                    pool_pre_ping=True,  # Verify connections before using
                )
                
                # Set up event listeners for connection management
                @event.listens_for(self._engine, "connect")
                def receive_connect(dbapi_conn, connection_record):
                    """Log new connections."""
                    logger.debug("New database connection established")
                
                @event.listens_for(self._engine, "checkout")
                def receive_checkout(dbapi_conn, connection_record, connection_proxy):
                    """Validate connection on checkout from pool."""
                    logger.debug("Connection checked out from pool")
                
                # Create session factory
                self._SessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self._engine
                )
                
                # Test the connection
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                logger.info("DB engine successfully initialized.")
                return
                
            except (OperationalError, DBAPIError) as e:
                logger.error(f"DB connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise ConnectionError(
                        "Failed to connect to PostgreSQL after multiple retries."
                    ) from e

    def get_session(self, retry: bool = True) -> Session:
        """
        Creates a new database session with retry logic.
        
        Args:
            retry: Whether to retry on connection failure (default: True)
            
        Returns:
            SQLAlchemy Session object
            
        Raises:
            ConnectionError: If unable to create session after retries
        """
        if not self._SessionLocal:
            raise ConnectionError("Database engine is not initialized.")
        
        attempts = self._max_retries if retry else 1
        
        for attempt in range(attempts):
            try:
                session = self._SessionLocal()
                
                # Validate session with a simple query
                try:
                    session.execute(text("SELECT 1"))
                except Exception as e:
                    logger.error(f"Session validation failed: {e}")
                    session.close()
                    raise
                
                return session
                
            except (OperationalError, DBAPIError) as e:
                logger.error(f"Session creation attempt {attempt + 1} failed: {e}")
                
                if attempt < attempts - 1:
                    wait_time = self._retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise ConnectionError(
                        f"Failed to create database session after {attempts} attempts"
                    ) from e

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        Automatically handles commits, rollbacks, and session cleanup.
        
        Usage:
            with db_service.session_scope() as session:
                user = User(name="John")
                session.add(user)
                # Auto-commits on exit if no exception
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rolled back due to error: {e}")
            raise
        finally:
            session.close()

    def execute_query(
        self,
        query: str,
        params: Optional[dict] = None,
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Any:
        """
        Execute a raw SQL query with automatic session management.
        
        Args:
            query: SQL query string
            params: Query parameters as dictionary
            fetch_one: Return single row
            fetch_all: Return all rows
            
        Returns:
            Query results or None
        """
        with self.session_scope() as session:
            result = session.execute(text(query), params or {})
            
            if fetch_one:
                return result.fetchone()
            elif fetch_all:
                return result.fetchall()
            else:
                return None

    def create_all_tables(self):
        """Create all tables defined in models that inherit from Base."""
        if not self._engine:
            raise ConnectionError("Database engine is not initialized.")
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self._engine)
        logger.info("Database tables created successfully.")

    def drop_all_tables(self):
        """Drop all tables (use with caution!)."""
        if not self._engine:
            raise ConnectionError("Database engine is not initialized.")
        
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self._engine)
        logger.info("All database tables dropped.")

    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database health check: OK")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def get_engine(self):
        """Returns the SQLAlchemy engine (for advanced use cases)."""
        return self._engine

    def close(self):
        """Dispose of the engine and close all connections."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine disposed and all connections closed.")


# Create singleton instance
db_service = DBService()


# Helper function for dependency injection (e.g., with FastAPI)
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for getting database sessions.
    
    Usage with FastAPI:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    session = db_service.get_session()
    try:
        yield session
    finally:
        session.close()