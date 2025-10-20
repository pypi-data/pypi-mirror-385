from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from godocs.cli import AppCommand


class Plugin(ABC):
    """
    This class allows the extension of the Godocs package
    by other packages that use the
    `[project.entry-points."godocs.plugins"]` field in their
    `pyproject.toml` to expose their `Plugin` implementation.
    """

    @abstractmethod
    def register(self, app: "AppCommand"):
        """
        This abstract method should be implemented to register
        new plugins to the Godocs package.
        """

        pass
