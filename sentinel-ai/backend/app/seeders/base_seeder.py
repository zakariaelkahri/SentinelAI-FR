from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any


class BaseSeeder(ABC):
    """
    Base class for all seeders
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def seed(self) -> None:
        """
        Main method to seed data
        Must be implemented by child classes
        """
        pass

    async def bulk_create(self, instances: List[Any]) -> None:
        """
        Bulk create multiple instances
        """
        self.session.add_all(instances)
        await self.session.flush()

    async def create(self, instance: Any) -> Any:
        """
        Create a single instance
        """
        self.session.add(instance)
        await self.session.flush()
        return instance

    def log(self, message: str) -> None:
        """
        Log seeder messages
        """
        print(f"[{self.__class__.__name__}] {message}")
