from os import PathLike
from .rst_syntax_translator import RSTSyntaxTranslator
from godocs.util import module


def get_translator(name: str | PathLike[str]):
    """
    Returns a `SyntaxTranslator` instance based on the `name` passed.

    Currently, the only supported translator is the `rst`.

    If it's desired to get a custom translator, its path can
    be passed in the `name` parameter.

    Custom translator should have a class called `SyntaxTranslator`
    which should extend the base `SyntaxTranslator` class.

    If no `SyntaxTranslator` class is exposed, a `NotImplementedError`
    is raised.
    """

    match name:
        case "rst": return RSTSyntaxTranslator()
        case _:
            try:
                return module.load("translator", name).SyntaxTranslator()
            except AttributeError:
                raise NotImplementedError(
                    "Translator not found. Custom translators should have a SyntaxTranslator class")
