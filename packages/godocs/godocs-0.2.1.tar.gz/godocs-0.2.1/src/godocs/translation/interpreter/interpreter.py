from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from godocs.translation import ast


class Interpreter(ABC):
    """
    Abstract class for interpreters that convert text into an
    abstract syntax tree (AST), returning a `TagNode`.

    Subclasses must implement the `interpret` method, which
    takes a string input and returns a `TagNode`
    representing the parsed syntax of the text.
    """

    @abstractmethod
    def interpret(self, text: str) -> "ast.TagNode":
        """
        Parse the input `text` and return a `TagNode`
        representing it in an AST.
        """

        pass
