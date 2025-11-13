"""
Database configuration and initialization for TezzaWorks Operations Dashboard
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
import os

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tezzaworks.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if 'sqlite' in DATABASE_URL else {},
    echo=True  # Set to False in production
)

# Create session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base class for models
Base = declarative_base()

def init_db():
    """Initialize database and create all tables"""
    from models.client import Client
    from models.product import Product
    from models.order import Order, OrderItem

    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

def drop_db():
    """Drop all tables from the database"""
    Base.metadata.drop_all(bind=engine)
    print("Database dropped successfully!")

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
