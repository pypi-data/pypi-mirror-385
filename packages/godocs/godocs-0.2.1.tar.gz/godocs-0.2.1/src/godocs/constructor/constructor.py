from abc import ABC, abstractmethod
from os import PathLike
from typing import Any


type ConstructorContext = dict[str, Any]


class Constructor(ABC):

    @abstractmethod
    def construct(self, context: ConstructorContext, path: str | PathLike[str]):
        pass
