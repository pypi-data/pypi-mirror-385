from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

import asyncpg
from asyncpg.pool import Pool

from ..database_conector import DatabaseConnector


class AsyncpgConnector(DatabaseConnector):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def fetch(self, query: str, *args, connection: Optional[asyncpg.Connection] = None) -> List[Dict[str, Any]]:
        if connection:
            return await connection.fetch(query, *args)
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchval(self, query: str, *args, connection: Optional[asyncpg.Connection] = None) -> Any:
        if connection:
            return await connection.fetchval(query, *args)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def execute(self, query: str, *args, connection: Optional[asyncpg.Connection] = None):
        if connection:
            await connection.execute(query, *args)
            return
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[asyncpg.Connection, None]:
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                yield connection
