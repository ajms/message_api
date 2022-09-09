import pytest

from src.helpers import get_redis, get_settings


@pytest.fixture
def r():
    yield get_redis()


@pytest.fixture
def cfg():
    yield get_settings()
