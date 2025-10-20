from unittest.mock import AsyncMock, MagicMock

import asyncpg
import pytest

from oop_es_pg.asyncpg.asyncpg_connector import AsyncpgConnector


class TestAsyncpgConnector:
    def setup_method(self):
        self.connection = AsyncMock(spec=asyncpg.Connection)
        self.pool = MagicMock()
        mock_acquire = AsyncMock()
        mock_acquire.__aenter__.return_value = self.connection
        mock_acquire.__aexit__.return_value = AsyncMock()
        self.pool.acquire.return_value = mock_acquire
        self.sut = AsyncpgConnector(pool=self.pool)

    @pytest.mark.asyncio
    async def test_fetch_with_connection(self):
        query = "SELECT * FROM table WHERE id = $1"
        params = (1,)
        expected_result = [{"id": 1, "name": "Test"}]
        self.connection.fetch.return_value = expected_result

        result = await self.sut.fetch(query, *params, connection=self.connection)

        self.connection.fetch.assert_awaited_with(query, *params)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_fetch_without_connection(self):
        query = "SELECT * FROM table"
        expected_result = [{"id": 1, "name": "Test"}]
        self.connection.fetch.return_value = expected_result

        result = await self.sut.fetch(query)

        self.pool.acquire.assert_called_once()
        self.connection.fetch.assert_awaited_with(query)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_fetchval_with_connection(self):
        self.pool.acquire.return_value = self.connection
        query = "SELECT name FROM table WHERE id = $1"
        params = (1,)
        expected_value = "Test"
        self.connection.fetchval.return_value = expected_value
        result = await self.sut.fetchval(query, *params, connection=self.connection)

        self.connection.fetchval.assert_awaited_with(query, *params)
        assert result == expected_value

    @pytest.mark.asyncio
    async def test_fetchval_without_connection(self):
        self.pool.acquire.return_value.__aenter__.return_value = self.connection
        query = "SELECT COUNT(*) FROM table"
        expected_value = 10
        self.connection.fetchval.return_value = expected_value

        result = await self.sut.fetchval(query)

        self.pool.acquire.assert_called_once()
        self.connection.fetchval.assert_awaited_with(query)
        assert result == expected_value

    @pytest.mark.asyncio
    async def test_execute_with_connection(self):
        self.pool.acquire.return_value = self.connection
        query = "INSERT INTO table (name) VALUES ($1)"
        params = ("Test",)

        await self.sut.execute(query, *params, connection=self.connection)

        self.connection.execute.assert_awaited_with(query, *params)

    @pytest.mark.asyncio
    async def test_execute_without_connection(self):
        self.pool.acquire.return_value.__aenter__.return_value = self.connection
        query = "DELETE FROM table WHERE id = $1"
        params = (1,)

        await self.sut.execute(query, *params)

        self.pool.acquire.assert_called_once()
        self.connection.execute.assert_awaited_with(query, *params)

    @pytest.mark.asyncio
    async def test_transaction(self):
        mock_transaction = AsyncMock()
        self.connection.transaction.return_value = mock_transaction
        self.pool.acquire.return_value.__aenter__.return_value = self.connection

        async with self.sut.transaction() as conn:
            assert conn == self.connection

        mock_transaction.__aenter__.assert_awaited_once()
        mock_transaction.__aexit__.assert_awaited_once()
