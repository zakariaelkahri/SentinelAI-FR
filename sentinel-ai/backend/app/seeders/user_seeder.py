from sqlalchemy import select
from passlib.context import CryptContext
from app.models.user import User, UserStatus
from app.models.role import Role
from app.models.admin import Admin
from app.models.operator import Operator
from app.models.supervisor import Supervisor
from .base_seeder import BaseSeeder


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserSeeder(BaseSeeder):
    """
    Seeder for User, Admin, Operator, and Supervisor models
    """

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)

    async def seed(self) -> None:
        """
        Seed users with their respective roles
        """
        self.log("Starting to seed users...")

        # Check if users already exist
        result = await self.session.execute(select(User))
        existing = result.scalars().all()

        if existing:
            self.log(f"Users already seeded ({len(existing)} found). Skipping...")
            return

        # Get roles
        roles_result = await self.session.execute(select(Role))
        roles = {role.name: role for role in roles_result.scalars().all()}

        if not roles:
            self.log("❌ Error: Roles must be seeded first!")
            return

        # Create Admin User
        admin_user = User(
            username="admin",
            password=self.hash_password("admin123"),  # Change in production!
            status=UserStatus.ACTIVE,
            role_id=roles["admin"].id,
        )
        await self.create(admin_user)

        admin_profile = Admin(
            user_id=admin_user.id,
        )
        await self.create(admin_profile)

        # Create Supervisor User
        supervisor_user = User(
            username="supervisor",
            password=self.hash_password("supervisor123"),  # Change in production!
            status=UserStatus.ACTIVE,
            role_id=roles["supervisor"].id,
        )
        await self.create(supervisor_user)

        supervisor_profile = Supervisor(
            user_id=supervisor_user.id,
        )
        await self.create(supervisor_profile)

        # Create Operator Users
        operators_data = ["operator1", "operator2"]

        for operator_name in operators_data:
            operator_user = User(
                username=operator_name,
                password=self.hash_password("operator123"),  # Change in production!
                status=UserStatus.ACTIVE,
                role_id=roles["operator"].id,
            )
            await self.create(operator_user)

            operator_profile = Operator(
                user_id=operator_user.id,
            )
            await self.create(operator_profile)

        await self.session.commit()

        self.log("✓ Successfully seeded users:")
        self.log("  - 1 Admin (username: admin, password: admin123)")
        self.log("  - 1 Supervisor (username: supervisor, password: supervisor123)")
        self.log("  - 2 Operators (username: operator1/operator2, password: operator123)")
        self.log("⚠️  IMPORTANT: Change default passwords in production!")
