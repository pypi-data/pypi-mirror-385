import json
from typing import Dict, List
from uuid import UUID

from asyncpg import UniqueViolationError

from oop_es import Event
from oop_es.event import Message
from oop_es.serializer.serializer import Serializer
from oop_es.store.event_store import EventStore
from oop_es.store.exception import WrongEventVersionException

from .database_conector import DatabaseConnector


class PostgresEventStore(EventStore):
    def __init__(self, connector: DatabaseConnector, event_serializer: Serializer, table: str = "events"):
        self.connector = connector
        self.table = table
        self.serializer = event_serializer

    async def load_events(self, aggregate_id: UUID) -> Dict[int, Event]:
        query = f"""
            SELECT version, event_data
            FROM {self.table}
            WHERE aggregate_id = $1
            ORDER BY version ASC
        """
        rows = await self.connector.fetch(query, str(aggregate_id))
        return {int(row["version"]): self.serializer.deserialize(json.loads(row["event_data"])) for row in rows}

    async def load_events_from(self, aggregate_id: UUID, version: int) -> Dict[int, Event]:
        query = f"""
            SELECT version, event_data
            FROM {self.table}
            WHERE aggregate_id = $1 AND version >= $2
            ORDER BY version ASC
        """
        rows = await self.connector.fetch(query, str(aggregate_id), version)
        return {int(row["version"]): self.serializer.deserialize(json.loads(row["event_data"])) for row in rows}

    async def add(self, messages: List[Message]):
        aggregate_id = None
        async with self.connector.transaction() as connection:
            for message in messages:
                if message.uuid != aggregate_id:
                    aggregate_id = message.uuid

                    current = await self.connector.fetchval(
                        f"SELECT MAX(version) FROM {self.table} WHERE aggregate_id = $1",
                        str(aggregate_id),
                        connection=connection,
                    )
                    current = current + 1 if current is not None else 0
                if message.version != current:
                    raise WrongEventVersionException(f"Wrong event version {message.version}, should be {current}")
                serialized_event = self.serializer.serialize(message.event)
                meta_json = json.dumps(message.meta)
                emitted_at_iso = message.emitted_at
                try:
                    await self.connector.execute(
                        f"""
                        INSERT INTO {self.table} (aggregate_id, version, event_data, meta, emitted_at)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        str(aggregate_id),
                        message.version,
                        json.dumps(serialized_event),
                        meta_json,
                        emitted_at_iso,
                        connection=connection,
                    )
                    current += 1
                except UniqueViolationError as exception:
                    raise WrongEventVersionException(f"Wrong event version {message.version}") from exception
