from sqlalchemy import select
from app.models.camera import Camera, CameraStatus
from app.models.operator import Operator
from app.models.user import User
from app.models.role import Role
from .base_seeder import BaseSeeder


class CameraSeeder(BaseSeeder):
    """
    Seeder for Camera model
    """

    async def seed(self) -> None:
        """
        Seed cameras
        """
        self.log("Starting to seed cameras...")

        # Check if cameras already exist
        result = await self.session.execute(select(Camera))
        existing = result.scalars().all()

        if existing:
            self.log(f"Cameras already seeded ({len(existing)} found). Skipping...")
            return

        # Get operators
        operators_result = await self.session.execute(
            select(Operator)
            .join(User)
            .join(Role)
            .where(Role.name == "operator")
        )
        operators = operators_result.scalars().all()

        if not operators:
            self.log("⚠️  Warning: No operators found. Creating cameras without assignment...")
            operator_id = None
        else:
            operator_id = operators[0].id

        # Define sample cameras
        cameras = [
            Camera(
                name="Main Entrance Camera",
                rtsp_url="rtsp://camera1.example.com:554/stream1",
                location="Main Building - Entrance",
                status=CameraStatus.ONLINE,
                operator_id=operator_id,
            ),
            Camera(
                name="Parking Lot Camera 1",
                rtsp_url="rtsp://camera2.example.com:554/stream1",
                location="Parking Lot - North Side",
                status=CameraStatus.ONLINE,
                operator_id=operator_id,
            ),
            Camera(
                name="Parking Lot Camera 2",
                rtsp_url="rtsp://camera3.example.com:554/stream1",
                location="Parking Lot - South Side",
                status=CameraStatus.OFFLINE,
                operator_id=operators[1].id if len(operators) > 1 else operator_id,
            ),
            Camera(
                name="Hallway Camera - Floor 1",
                rtsp_url="rtsp://camera4.example.com:554/stream1",
                location="Building A - Floor 1 Hallway",
                status=CameraStatus.ONLINE,
                operator_id=operators[1].id if len(operators) > 1 else operator_id,
            ),
            Camera(
                name="Server Room Camera",
                rtsp_url="rtsp://camera5.example.com:554/stream1",
                location="Building A - Server Room",
                status=CameraStatus.MAINTENANCE,
                operator_id=None,  # Unassigned
            ),
        ]

        await self.bulk_create(cameras)
        await self.session.commit()

        self.log(f"✓ Successfully seeded {len(cameras)} cameras")
