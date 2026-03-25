"""
Database Seeder Script

This script runs all seeders in the correct order to populate
the database with initial data.

Usage:
    python -m app.seeders.seed
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.seeders.permission_seeder import PermissionSeeder
from app.seeders.role_seeder import RoleSeeder
from app.seeders.user_seeder import UserSeeder
from app.seeders.camera_seeder import CameraSeeder


async def run_seeders():
    """
    Run all seeders in the correct order
    """
    print("=" * 60)
    print("Starting Database Seeding...")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            # Run seeders in order (respecting foreign key dependencies)
            seeders = [
                PermissionSeeder(session),
                RoleSeeder(session),
                UserSeeder(session),
                CameraSeeder(session),
            ]

            for seeder in seeders:
                await seeder.seed()

            print("\n" + "=" * 60)
            print("✅ Database seeding completed successfully!")
            print("=" * 60)

        except Exception as e:
            print("\n" + "=" * 60)
            print(f"❌ Error during seeding: {str(e)}")
            print("=" * 60)
            await session.rollback()
            raise
        finally:
            await session.close()


def main():
    """
    Main entry point
    """
    asyncio.run(run_seeders())


if __name__ == "__main__":
    main()
