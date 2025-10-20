from os import PathLike
from godocs.util import module
from warnings import deprecated


@deprecated("Old way of choosing constructor implementation. Use plugins instead.")
def get_constructor(name: str | PathLike[str]):
    """
    Returns a `Constructor` instance based on the `name` passed.

    Currently, the only supported constructors is the `jinja`.

    If it's desired to get a custom constructor, its path can
    be passed in the `name` parameter.

    Custom constructors should have a class called `Constructor`
    which should extend the base `Constructor` class.

    If no `Constructor` class is exposed, a `NotImplementedError`
    is raised.
    """

    match name:
        case "jinja": return  # JinjaConstructor()
        case _:
            try:
                return module.load("constructor", name).Constructor()
            except AttributeError:
                raise NotImplementedError(
                    "Constructor not found. Custom constructors should have a Constructor class")
