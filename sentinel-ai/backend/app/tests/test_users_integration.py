import uuid
from types import SimpleNamespace

from app.models.user import UserStatus


def test_users_admin_create_user_operator(
    client_factory,
    fake_async_session_cls,
    fake_result_cls,
    build_test_user_fn,
):
    admin_user = build_test_user_fn("admin", "admin")
    operator_role = SimpleNamespace(id=uuid.uuid4(), name="operator")
    fake_db = fake_async_session_cls(
        execute_results=[
            fake_result_cls(scalar=None),  # existing username lookup
            fake_result_cls(scalar=operator_role),  # role lookup
        ],
    )

    client = client_factory(fake_db, admin_user)
    response = client.post(
        "/users/admin/create-user",
        json={
            "username": "operator3",
            "password": "operator123",
            "role": "operator",
            "status": "active",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "operator3"
    assert body["role"] == "operator"
    assert body["status"] == "active"
    assert body["created_by"] == str(admin_user.id)
    assert body["profile_id"] is not None


def test_users_admin_list_managed_users(
    client_factory,
    fake_async_session_cls,
    fake_result_cls,
    build_test_user_fn,
):
    admin_user = build_test_user_fn("admin", "admin")
    managed_user_id = uuid.uuid4()
    operator_profile_id = uuid.uuid4()

    fake_db = fake_async_session_cls(
        execute_results=[
            fake_result_cls(rows=[(managed_user_id, "operator1", UserStatus.ACTIVE, "operator")]),
            fake_result_cls(rows=[(managed_user_id, operator_profile_id)]),
            fake_result_cls(rows=[]),
        ],
    )

    client = client_factory(fake_db, admin_user)
    response = client.get("/users/admin/users")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == str(managed_user_id)
    assert body[0]["role"] == "operator"
    assert body[0]["profile_id"] == str(operator_profile_id)


def test_users_admin_update_managed_user_status(
    client_factory,
    fake_async_session_cls,
    fake_result_cls,
    build_test_user_fn,
):
    admin_user = build_test_user_fn("admin", "admin")
    managed_user_id = uuid.uuid4()
    operator_profile_id = uuid.uuid4()

    managed_user = SimpleNamespace(
        id=managed_user_id,
        username="operator1",
        password="hashed-password",
        status=UserStatus.ACTIVE,
        role_id=uuid.uuid4(),
    )

    fake_db = fake_async_session_cls(
        execute_results=[
            fake_result_cls(first=(managed_user, "operator")),
            fake_result_cls(scalar=operator_profile_id),
        ],
    )

    client = client_factory(fake_db, admin_user)
    response = client.patch(
        f"/users/admin/users/{managed_user_id}",
        json={"status": "inactive"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(managed_user_id)
    assert body["status"] == "inactive"
    assert body["role"] == "operator"
    assert body["profile_id"] == str(operator_profile_id)
