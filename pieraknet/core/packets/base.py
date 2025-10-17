from abc import ABC, abstractmethod
from typing import Self


class BasePacket(ABC):
    @abstractmethod
    def serialize(self) -> bytes: ...

    @abstractmethod
    @classmethod
    def deserialize(cls, data: bytes) -> Self: ...

    def __eq__(self, other) -> bool:
        if not hasattr(other, "__repr__"):
            return False
        return repr(self) == repr(other)
