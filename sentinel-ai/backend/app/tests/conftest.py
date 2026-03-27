from types import SimpleNamespace
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import assistant as assistant_api
from app.api import auth as auth_api
from app.api import users as users_api
from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import UserStatus


class FakeScalars:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class FakeResult:
    def __init__(self, *, scalar=None, first=None, rows=None):
        self._scalar = scalar
        self._first = first
        self._rows = rows or []

    def scalar_one_or_none(self):
        return self._scalar

    def first(self):
        return self._first

    def all(self):
        return self._rows

    def scalars(self):
        return FakeScalars(self._rows)


class FakeAsyncSession:
    def __init__(self, execute_results=None):
        self._execute_results = list(execute_results or [])
        self._added = []

    async def execute(self, _query):
        if not self._execute_results:
            raise AssertionError("Unexpected database execute() call in test")
        return self._execute_results.pop(0)

    def add(self, obj):
        self._added.append(obj)

    async def flush(self):
        for obj in self._added:
            if getattr(obj, "id", None) is None:
                setattr(obj, "id", uuid.uuid4())

    async def refresh(self, _obj):
        return None

    async def delete(self, _obj):
        return None


def build_test_user(username: str, role_name: str):
    return SimpleNamespace(
        id=uuid.uuid4(),
        username=username,
        password="hashed-password",
        status=UserStatus.ACTIVE,
        role=SimpleNamespace(name=role_name),
        last_login=None,
    )


@pytest.fixture
def app_factory():
    def _create(fake_db, current_user):
        app = FastAPI()
        app.include_router(auth_api.router)
        app.include_router(assistant_api.router)
        app.include_router(users_api.router)

        async def override_get_db():
            yield fake_db

        async def override_get_current_user():
            return current_user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_active_user] = override_get_current_user
        return app

    return _create


@pytest.fixture
def client_factory(app_factory):
    def _create(fake_db, current_user):
        app = app_factory(fake_db, current_user)
        return TestClient(app)

    return _create


@pytest.fixture
def fake_async_session_cls():
    return FakeAsyncSession


@pytest.fixture
def fake_result_cls():
    return FakeResult


@pytest.fixture
def build_test_user_fn():
    return build_test_user
