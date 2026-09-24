import os
import sys
import pytest

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Tests must be deterministic and must never spend money or depend on a remote LLM.
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("ALLOW_MOCK_FALLBACK", "False")

from app.core.config import settings
from app.database.session import init_db

settings.LLM_PROVIDER = "mock"
settings.ALLOW_MOCK_FALLBACK = False

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    init_db()
