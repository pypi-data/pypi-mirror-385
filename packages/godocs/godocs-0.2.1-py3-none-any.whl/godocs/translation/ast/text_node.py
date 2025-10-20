from .node import Node
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from godocs.translation.translator import SyntaxTranslator


class TextNode(Node):
    """
    Class representing a node with text content in an abstract syntax tree used
    for syntax translation (AST).

    This class expects that its text `content` is passed in order
    for it to be constructed.
    """

    def __init__(self, content: str):
        self.content = content

    def translate(self, translator: "SyntaxTranslator") -> str:
        """
        Translates this `TextNode` into a `string` using the provided `SyntaxTranslator`.
        """

        return translator.translate_text(self)

    def __str__(self) -> str:
        return f'"{self.content}"'
