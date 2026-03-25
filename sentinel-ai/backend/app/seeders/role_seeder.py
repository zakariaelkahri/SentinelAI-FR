from sqlalchemy import select
from app.models.role import Role
from .base_seeder import BaseSeeder


class RoleSeeder(BaseSeeder):
    """
    Seeder for Role model
    """

    async def seed(self) -> None:
        """
        Seed roles
        """
        self.log("Starting to seed roles...")

        # Check if roles already exist
        result = await self.session.execute(select(Role))
        existing = result.scalars().all()

        if existing:
            self.log(f"Roles already seeded ({len(existing)} found). Skipping...")
            return

        # Define roles
        roles = [
            Role(name="admin"),
            Role(name="supervisor"),
            Role(name="operator"),
        ]

        await self.bulk_create(roles)
        await self.session.commit()

        self.log(f"✓ Successfully seeded {len(roles)} roles")
