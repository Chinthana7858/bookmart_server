
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import Base, get_db

# Use SQLite test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Recreate the DB for each test session
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override get_db in app
@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
