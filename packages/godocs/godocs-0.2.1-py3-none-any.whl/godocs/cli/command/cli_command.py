from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import Optional, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from argparse import _SubParsersAction  # type: ignore

type Processor = Callable[[Namespace], Namespace]


class CLICommand(ABC):
    """
    Base class that represents a CLI command or subcommand.

    The `register` method should be implemented to connect
    the logic of this command as an `argparse` parser or
    subparser.
    """

    @abstractmethod
    def register(
        self,
        superparsers: "Optional[_SubParsersAction[ArgumentParser]]" = None,
        parent_parser: Optional[ArgumentParser] = None,
        processors: Optional[list[Processor]] = None
    ):
        """
        Abstract method that takes a `subparsers` instance
        (from `argparse.ArgumentParser.add_subparsers`) and
        should append a subparser to them.

        For a root command implementation, the `subparsers`
        parameter may be null, since it isn't a subparser
        as opposed to a main parser.
        """
        pass

    @abstractmethod
    def execute(self, args: Namespace):
        pass

    def process(self, args: Namespace) -> Namespace:
        return args
