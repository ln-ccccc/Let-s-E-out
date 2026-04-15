import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app_client() -> TestClient:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("APP_JWT_SECRET", "test-secret")
    os.environ.setdefault("APP_JWT_EXPIRES_MINUTES", "60")
    os.environ.setdefault("APP_DATABASE_URL", "sqlite+pysqlite:///./test.db")

    from app.main import app
    from app.db.base import Base
    from app.db.session import engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    return TestClient(app)
