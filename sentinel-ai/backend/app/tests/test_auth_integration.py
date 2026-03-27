from app.api import auth as auth_api


def test_auth_login_success_returns_token_and_user(
    client_factory,
    monkeypatch,
    fake_async_session_cls,
    fake_result_cls,
    build_test_user_fn,
):
    user = build_test_user_fn("admin", "admin")
    fake_db = fake_async_session_cls(
        execute_results=[fake_result_cls(scalar=user)],
    )

    monkeypatch.setattr(auth_api, "verify_password", lambda plain, hashed: True)
    monkeypatch.setattr(auth_api, "create_access_token", lambda data, expires_delta: "jwt-token")

    client = client_factory(fake_db, user)
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "jwt-token"
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "admin"


def test_auth_login_invalid_credentials_returns_401(
    client_factory,
    fake_async_session_cls,
    fake_result_cls,
    build_test_user_fn,
):
    current_user = build_test_user_fn("admin", "admin")
    fake_db = fake_async_session_cls(
        execute_results=[fake_result_cls(scalar=None)],
    )

    client = client_factory(fake_db, current_user)
    response = client.post(
        "/auth/login",
        json={"username": "ghost", "password": "wrong12"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_auth_me_returns_current_user_profile(
    client_factory,
    fake_async_session_cls,
    build_test_user_fn,
):
    user = build_test_user_fn("operator1", "operator")
    fake_db = fake_async_session_cls()

    client = client_factory(fake_db, user)
    response = client.get("/auth/me")

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "operator1"
    assert body["role_name"] == "operator"
