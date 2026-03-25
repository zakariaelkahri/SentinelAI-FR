import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_active_user, require_role
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.camera import Camera
from app.models.operator import Operator
from app.models.role import Role
from app.models.supervisor import Supervisor
from app.models.user import User, UserStatus
from app.schemas.user import (
    AdminCreateUserRequest,
    AdminCreatedUserResponse,
    AdminManagedUserResponse,
    AdminUpdateUserRequest,
)


router = APIRouter(prefix="/users", tags=["Users"])
MANAGED_ROLES = {"operator", "supervisor"}


async def _resolve_role(db: AsyncSession, role_name: str) -> Role:
    role_result = await db.execute(select(Role).where(Role.name == role_name))
    role = role_result.scalar_one_or_none()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name}' not found",
        )
    return role


async def _resolve_profile_id(
    db: AsyncSession, user_id, role_name: str
):
    if role_name == "operator":
        operator_result = await db.execute(select(Operator.id).where(Operator.user_id == user_id))
        return operator_result.scalar_one_or_none()

    supervisor_result = await db.execute(
        select(Supervisor.id).where(Supervisor.user_id == user_id)
    )
    return supervisor_result.scalar_one_or_none()


@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user's profile

    Protected route - requires authentication
    """
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "status": current_user.status.value,
        "role": current_user.role.name if current_user.role else None,
        "last_login": current_user.last_login
    }


@router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
async def admin_only_route():
    """
    Admin only route example

    Protected route - requires admin role
    """
    return {"message": "This is an admin-only endpoint"}


@router.get("/operator-supervisor", dependencies=[Depends(require_role("operator", "supervisor"))])
async def operator_supervisor_route():
    """
    Operator or Supervisor route example

    Protected route - requires operator or supervisor role
    """
    return {"message": "This endpoint is accessible by operators and supervisors"}


@router.post(
    "/admin/create-user",
    response_model=AdminCreatedUserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def admin_create_operator_or_supervisor(
    request_data: AdminCreateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Admin-only endpoint to create operator or supervisor accounts.
    """
    existing_user_result = await db.execute(
        select(User).where(User.username == request_data.username)
    )
    if existing_user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    role = await _resolve_role(db, request_data.role)

    user = User(
        username=request_data.username,
        password=get_password_hash(request_data.password),
        status=UserStatus(request_data.status),
        role_id=role.id,
    )
    db.add(user)
    await db.flush()

    if request_data.role == "operator":
        profile = Operator(user_id=user.id)
        db.add(profile)
    else:
        profile = Supervisor(user_id=user.id)
        db.add(profile)

    await db.flush()

    return AdminCreatedUserResponse(
        id=user.id,
        username=user.username,
        role=request_data.role,
        status=user.status.value,
        profile_id=profile.id,
        created_by=current_user.id,
    )


@router.get(
    "/admin/users",
    response_model=list[AdminManagedUserResponse],
    dependencies=[Depends(require_role("admin"))],
)
async def admin_list_managed_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ = current_user

    user_rows_result = await db.execute(
        select(User.id, User.username, User.status, Role.name)
        .join(Role, User.role_id == Role.id)
        .where(Role.name.in_(tuple(MANAGED_ROLES)))
        .order_by(User.username.asc())
    )
    user_rows = user_rows_result.all()
    if not user_rows:
        return []

    user_ids = [user_id for user_id, _, _, _ in user_rows]
    operator_rows_result = await db.execute(
        select(Operator.user_id, Operator.id).where(Operator.user_id.in_(user_ids))
    )
    supervisor_rows_result = await db.execute(
        select(Supervisor.user_id, Supervisor.id).where(Supervisor.user_id.in_(user_ids))
    )
    operator_ids_by_user = {user_id: profile_id for user_id, profile_id in operator_rows_result.all()}
    supervisor_ids_by_user = {
        user_id: profile_id for user_id, profile_id in supervisor_rows_result.all()
    }

    response = []
    for user_id, username, user_status, role_name in user_rows:
        profile_id = (
            operator_ids_by_user.get(user_id)
            if role_name == "operator"
            else supervisor_ids_by_user.get(user_id)
        )
        response.append(
            AdminManagedUserResponse(
                id=user_id,
                username=username,
                role=role_name,
                status=user_status.value,
                profile_id=profile_id,
            )
        )

    return response


@router.patch(
    "/admin/users/{user_id}",
    response_model=AdminManagedUserResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def admin_update_managed_user(
    user_id: uuid.UUID,
    request_data: AdminUpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ = current_user

    updates = request_data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    user_row_result = await db.execute(
        select(User, Role.name)
        .join(Role, User.role_id == Role.id)
        .where(User.id == user_id)
    )
    user_row = user_row_result.first()
    if user_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user, current_role_name = user_row
    if current_role_name not in MANAGED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only operator or supervisor users can be edited here",
        )

    if "username" in updates and updates["username"] != user.username:
        existing_user_result = await db.execute(
            select(User).where(User.username == updates["username"])
        )
        if existing_user_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )
        user.username = updates["username"]

    if "password" in updates and updates["password"] is not None:
        user.password = get_password_hash(updates["password"])

    if "status" in updates and updates["status"] is not None:
        user.status = UserStatus(updates["status"])

    target_role_name = updates.get("role", current_role_name)
    if target_role_name not in MANAGED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be operator or supervisor",
        )

    if target_role_name != current_role_name:
        target_role = await _resolve_role(db, target_role_name)
        user.role_id = target_role.id

        operator_result = await db.execute(select(Operator).where(Operator.user_id == user.id))
        operator_profile = operator_result.scalar_one_or_none()
        supervisor_result = await db.execute(
            select(Supervisor).where(Supervisor.user_id == user.id)
        )
        supervisor_profile = supervisor_result.scalar_one_or_none()

        if target_role_name == "supervisor":
            if operator_profile is not None:
                assigned_cameras_result = await db.execute(
                    select(Camera).where(Camera.operator_id == operator_profile.id)
                )
                assigned_cameras = assigned_cameras_result.scalars().all()
                for camera in assigned_cameras:
                    camera.operator_id = None
                await db.flush()
                await db.delete(operator_profile)

            if supervisor_profile is None:
                db.add(Supervisor(user_id=user.id))
        else:
            if supervisor_profile is not None:
                await db.delete(supervisor_profile)

            if operator_profile is None:
                db.add(Operator(user_id=user.id))

    await db.flush()

    profile_id = await _resolve_profile_id(db, user.id, target_role_name)

    return AdminManagedUserResponse(
        id=user.id,
        username=user.username,
        role=target_role_name,
        status=user.status.value,
        profile_id=profile_id,
    )
