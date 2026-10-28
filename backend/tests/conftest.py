import pytest
from app.database.session import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()
