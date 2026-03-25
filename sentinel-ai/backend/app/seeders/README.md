# Database Seeders

This directory contains database seeders to populate your SentinelAI database with initial data.

## Structure

```
seeders/
├── __init__.py              # Package initialization
├── base_seeder.py           # Base seeder class with common functionality
├── permission_seeder.py     # Seeds permissions
├── role_seeder.py           # Seeds roles (admin, supervisor, operator)
├── user_seeder.py           # Seeds users with their profiles
├── camera_seeder.py         # Seeds sample cameras
├── seed.py                  # Main seeder script
└── README.md               # This file
```

## Usage

### Run All Seeders

From the backend directory:

```bash
python -m app.seeders.seed
```

Or with Docker:

```bash
docker exec -it sentinel-backend python -m app.seeders.seed
```

### Seeding Order

Seeders are executed in this order to respect foreign key dependencies:

1. **PermissionSeeder** - Creates permissions (no dependencies)
2. **RoleSeeder** - Creates roles: admin, supervisor, operator (no dependencies)
3. **UserSeeder** - Creates users with their profiles (depends on roles)
4. **CameraSeeder** - Creates sample cameras (depends on operators)

## Default Seeded Data

### Roles
- `admin` - Administrator role
- `supervisor` - Supervisor role
- `operator` - Operator role

### Permissions
Full CRUD permissions for:
- Users
- Roles
- Cameras
- Alerts
- Incident Reports
- Analytics & Reports
- System Settings

### Users

| Username   | Password      | Role       |
|------------|---------------|------------|
| admin      | admin123      | admin      |
| supervisor | supervisor123 | supervisor |
| operator1  | operator123   | operator   |
| operator2  | operator123   | operator   |

**⚠️ IMPORTANT:** Change these default passwords in production!

### Cameras
5 sample cameras with different statuses:
- Main Entrance Camera (Online)
- Parking Lot Camera 1 (Online)
- Parking Lot Camera 2 (Offline)
- Hallway Camera - Floor 1 (Online)
- Server Room Camera (Maintenance)

## Features

### Idempotent Seeding
All seeders check if data already exists before seeding. Running seeders multiple times won't create duplicate data - existing data will be skipped.

### Database Transactions
Each seeder commits its changes after successful completion. If an error occurs, changes are rolled back.

## Creating New Seeders

To create a new seeder:

1. Create a new file: `your_model_seeder.py`
2. Extend the `BaseSeeder` class:

```python
from sqlalchemy import select
from app.models.your_model import YourModel
from .base_seeder import BaseSeeder


class YourModelSeeder(BaseSeeder):
    async def seed(self) -> None:
        self.log("Starting to seed your model...")

        # Check if already seeded
        result = await self.session.execute(select(YourModel))
        existing = result.scalars().all()

        if existing:
            self.log(f"Already seeded ({len(existing)} found). Skipping...")
            return

        # Create your data
        items = [
            YourModel(field1="value1"),
            YourModel(field2="value2"),
        ]

        await self.bulk_create(items)
        await self.session.commit()

        self.log(f"✓ Successfully seeded {len(items)} items")
```

3. Add to `seed.py`:

```python
from app.seeders.your_model_seeder import YourModelSeeder

# In run_seeders():
seeders = [
    # ... existing seeders ...
    YourModelSeeder(session),
]
```

## Troubleshooting

### "Roles must be seeded first"
Make sure you run all seeders together, or run RoleSeeder before UserSeeder.

### Foreign Key Constraint Errors
Check the seeding order - dependent models must be seeded after their dependencies.

### "Already seeded" message
This is normal - seeders skip if data already exists. To force re-seed, manually delete the existing data first.
