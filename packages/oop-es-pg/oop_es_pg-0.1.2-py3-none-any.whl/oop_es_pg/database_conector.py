from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional


class DatabaseConnector(ABC):
    @abstractmethod
    async def fetch(self, query: str, *args, connection: Optional[Any] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def fetchval(self, query: str, *args, connection: Optional[Any] = None) -> Any:
        pass

    @abstractmethod
    async def execute(self, query: str, *args, connection: Optional[Any] = None):
        pass

    @abstractmethod
    async def transaction(self) -> AsyncGenerator[Any, None]:
        pass
