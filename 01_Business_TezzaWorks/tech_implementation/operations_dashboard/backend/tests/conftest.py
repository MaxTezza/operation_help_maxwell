import pytest
from app import create_app
from database import init_db, drop_db, SessionLocal
from seed_data import seed_data

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for the test session."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture(scope='function')
def db(app):
    """Create and drop database for each test function."""
    with app.app_context():
        init_db()
        yield SessionLocal()
        drop_db()

@pytest.fixture(scope='function')
def client(app, db):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def seeded_db(db):
    """Seed the database with sample data."""
    seed_data(db)
    return db

@pytest.fixture(scope='function')
def seeded_client(app, seeded_db):
    """A test client for the app with a seeded database."""
    return app.test_client()
