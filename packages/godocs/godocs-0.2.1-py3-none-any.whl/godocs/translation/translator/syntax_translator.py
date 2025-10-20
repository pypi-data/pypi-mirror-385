from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from godocs.translation import ast


class SyntaxTranslator(ABC):
    """
    Abstract base class for translating `ast` nodes.

    This class defines a interface for translating two types of
    nodes into string representations: the `TextNode` and the `TagNode`.

    Subclasses must implement the `translate_text` and `translate_tag` methods
    for defining how those nodes should be translated.
    """

    @abstractmethod
    def translate_text(self, node: "ast.TextNode") -> str:
        """
        Abstract method to translate a `TextNode` into its string representation.
        """

        pass

    @abstractmethod
    def translate_tag(self, node: "ast.TagNode") -> str:
        """
        Abstract method to translate a `TagNode` into its string representation.
        """

        pass
