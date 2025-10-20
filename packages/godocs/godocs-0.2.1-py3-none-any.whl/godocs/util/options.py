import json
from os import PathLike


def load(path: str | PathLike[str]):
    """
    Loads a **JSON file** located in `path` and
    parses its values to a `dict` variable.

    The loaded `dict` is then returned.
    """

    with open(path, "r", encoding="utf-8") as f:
        options = json.load(f)

    return options
