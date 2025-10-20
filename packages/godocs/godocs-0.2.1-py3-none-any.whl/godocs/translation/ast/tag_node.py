from textwrap import indent
from typing import TYPE_CHECKING

from .node import Node

if TYPE_CHECKING:
    from godocs.translation.translator import SyntaxTranslator


class TagNode(Node):
    """
    Class representing a node that can hold other `Nodes` as content
    in an abstract syntax tree used for syntax translation (AST).

    Besides its `children`, the `TagNode` class can have a `name` -
    to identify its type - and `params` - to store specific data.
    All of these properties are expected to be passed on construction.
    """

    def __init__(
        self,
        name: str,
        children: list[Node] | None = None,
        params: dict[str, str] | None = None,
    ):
        if children is None:
            children = []
        if params is None:
            params = {}

        self.name = name
        self.children = children
        self.params = params

    def translate(self, translator: "SyntaxTranslator") -> str:
        return translator.translate_tag(self)

    def stringify_params(self) -> str:
        result = ""

        for i, key in enumerate(self.params):
            value = self.params[key]

            result += f"{key}={value}"

            if i < len(self.params) - 1:
                result += ", "

        return result

    def stringify_children(self) -> str:
        result = ""

        for i, child in enumerate(self.children):
            result += str(child)

            if i < len(self.children) - 1:
                result += ",\n"

        return result

    def __str__(self) -> str:
        result = f"<{self.name}"

        if not len(self.params) == 0:
            result += f" {self.stringify_params()}"

        if not len(self.children) == 0:
            result += indent(f"\n{self.stringify_children()}\n", "\t")

        result += '>'

        return result
