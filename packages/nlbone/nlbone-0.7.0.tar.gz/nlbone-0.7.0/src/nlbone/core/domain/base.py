from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, List, TypeVar
from uuid import uuid4

from pydantic import BaseModel

TId = TypeVar("TId")


class DomainError(Exception):
    """Base domain exception."""



class Message(BaseModel):
    pass



class DomainEvent(Message):
    """Immutable domain event."""

    occurred_at: datetime = datetime.now(timezone.utc)
    event_id: str = uuid4()

    @property
    def name(self):
        return self.__class__.__name__


@dataclass(frozen=True)
class Command:
    pass


class ValueObject:
    """Base for value objects (immutable in practice)."""

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __hash__(self) -> int:  # allow in sets/dicts
        return hash(tuple(sorted(self.__dict__.items())))


class Entity(Generic[TId]):
    id: TId


class AggregateRoot(Entity[TId]):
    """Aggregate root with domain event collection."""

    def __init__(self) -> None:
        self._events: List[DomainEvent] = []

    @property
    def events(self) -> List[DomainEvent]:
        return self._events

    def _raise(self, event: DomainEvent) -> None:
        self._events.append(event)

    def clear_events(self) -> None:
        self._events.clear()


class BaseEnum(Enum):
    pass
