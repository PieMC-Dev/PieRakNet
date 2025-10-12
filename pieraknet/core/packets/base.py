from abc import ABC, abstractmethod
from typing import Self


class BasePacket(ABC):
    @abstractmethod
    def serialize(self) -> bytes:
        ...
    
    @abstractmethod
    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        ...
