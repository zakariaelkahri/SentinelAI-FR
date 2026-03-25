from sqlalchemy import select
from app.models.permission import Permission
from .base_seeder import BaseSeeder


class PermissionSeeder(BaseSeeder):
    """
    Seeder for Permission model
    """

    async def seed(self) -> None:
        """
        Seed permissions
        """
        self.log("Starting to seed permissions...")

        # Check if permissions already exist
        result = await self.session.execute(select(Permission))
        existing = result.scalars().all()

        if existing:
            self.log(f"Permissions already seeded ({len(existing)} found). Skipping...")
            return

        # Define permissions
        permissions = [
            # User Management
            Permission(name="user.create"),
            Permission(name="user.read"),
            Permission(name="user.update"),
            Permission(name="user.delete"),
            Permission(name="user.list"),

            # Role Management
            Permission(name="role.create"),
            Permission(name="role.read"),
            Permission(name="role.update"),
            Permission(name="role.delete"),
            Permission(name="role.list"),

            # Camera Management
            Permission(name="camera.create"),
            Permission(name="camera.read"),
            Permission(name="camera.update"),
            Permission(name="camera.delete"),
            Permission(name="camera.list"),
            Permission(name="camera.monitor"),

            # Alert Management
            Permission(name="alert.create"),
            Permission(name="alert.read"),
            Permission(name="alert.update"),
            Permission(name="alert.delete"),
            Permission(name="alert.list"),
            Permission(name="alert.acknowledge"),

            # Incident Report Management
            Permission(name="incident.create"),
            Permission(name="incident.read"),
            Permission(name="incident.update"),
            Permission(name="incident.delete"),
            Permission(name="incident.list"),
            Permission(name="incident.approve"),

            # Analytics & Reports
            Permission(name="analytics.view"),
            Permission(name="reports.generate"),
            Permission(name="reports.export"),

            # System Settings
            Permission(name="settings.read"),
            Permission(name="settings.update"),
        ]

        await self.bulk_create(permissions)
        await self.session.commit()

        self.log(f"✓ Successfully seeded {len(permissions)} permissions")
