import asyncio
from dataclasses import dataclass
from uuid import uuid4

import asyncpg
import pytest
import pytest_asyncio

from oop_es import Event
from oop_es.event import Message
from oop_es.serializer.event_serializer import EventSerializer
from oop_es.store.exception import WrongEventVersionException
from oop_es_pg import PostgresEventStore
from oop_es_pg.asyncpg.asyncpg_connector import AsyncpgConnector


@dataclass
class DummyEvent(Event):
    x: int
    y: str


@pytest_asyncio.fixture
async def connector():
    dsn = "postgresql://event_user:event_pass@localhost:35432/event_store_db"
    conn = AsyncpgConnector(await asyncpg.create_pool(dsn=dsn))
    return conn


@pytest_asyncio.fixture(name="store")
async def event_store(connector):
    store = PostgresEventStore(connector, EventSerializer())
    await asyncio.sleep(0)
    return store


@pytest.mark.asyncio
async def test_load_events_empty(store):
    aggregate_id = uuid4()

    result = await store.load_events(aggregate_id)

    assert result == {}


@pytest.mark.asyncio
async def test_load_events(store):
    aggregate_id = uuid4()
    event1 = DummyEvent(x=1, y="abc")
    event2 = DummyEvent(x=3, y="def")
    await store.add([Message(aggregate_id, event1, 0), Message(aggregate_id, event2, 1)])

    result = await store.load_events(aggregate_id)

    assert result == {0: event1, 1: event2}


@pytest.mark.asyncio
async def test_load_events_from(store):
    aggregate_id = uuid4()
    event1 = Event()
    event2 = Event()
    event3 = Event()
    await store.add([Message(aggregate_id, event1, 0), Message(aggregate_id, event2, 1), Message(aggregate_id, event3, 2),])

    result = await store.load_events_from(aggregate_id, 1)

    assert result == {1: event2, 2: event3}


@pytest.mark.asyncio
async def test_add_events_with_wrong_version(store):
    aggregate_id = uuid4()
    event1 = Event()
    event2 = Event()

    await store.add([Message(aggregate_id, event1, 0)])

    with pytest.raises(WrongEventVersionException):
        await store.add([Message(aggregate_id, event1, 0)])

    with pytest.raises(WrongEventVersionException):
        await store.add([Message(aggregate_id, event2, 2)])
