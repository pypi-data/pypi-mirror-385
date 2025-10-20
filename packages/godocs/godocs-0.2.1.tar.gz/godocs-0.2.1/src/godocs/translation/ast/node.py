from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from godocs.translation.translator import SyntaxTranslator


class Node(ABC):
    """
    Abstract base class representing a node in an abstract syntax tree used
    for syntax translation (AST).

    Subclasses must implement the `translate` method, which defines how the node should be
    translated using a provided `SyntaxTranslator`.

    The general protocol for syntax representation using the `godocs.translation.ast`
    module is described below:

    - The topmost node should be a `TagNode` with name `root`;

    - Tags that reference documentation members should be called `reference` and
    have the type of member they reference annotated in the `type` param.
    The name of the referenced member should be stored in the `name` param.
    In the case the referenced member is an `operator`, it should also have
    its operator stored in the `symbol` param.
    If the referenced member is just a `param`, the its AST tag may be a `code`.

    TODO: finish protocol documentation.
    """

    @abstractmethod
    def translate(self, translator: "SyntaxTranslator") -> str:
        """
        Abstract method to translate this `Node` using a given `translator`.
        """

        pass
