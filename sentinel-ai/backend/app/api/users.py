from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_active_user, require_role
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.operator import Operator
from app.models.role import Role
from app.models.supervisor import Supervisor
from app.models.user import User, UserStatus
from app.schemas.user import AdminCreateUserRequest, AdminCreatedUserResponse


router = APIRouter(prefix="/users", tags=["Users"])


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

    role_result = await db.execute(select(Role).where(Role.name == request_data.role))
    role = role_result.scalar_one_or_none()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{request_data.role}' not found",
        )

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
