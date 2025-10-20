from importlib.metadata import entry_points
from typing import Any


def load() -> list[Any]:
    """
    Loads all plugin entry points registered under the `godocs.plugin`
    group and instantiates them, storing their result in the
    returned `list`.
    """

    plugins: list[Any] = []

    for ep in entry_points(group="godocs.plugins"):
        Plugin = ep.load()

        plugins.append(Plugin())

    return plugins
