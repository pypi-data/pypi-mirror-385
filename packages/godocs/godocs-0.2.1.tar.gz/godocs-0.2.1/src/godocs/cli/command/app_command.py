from argparse import ArgumentParser, Namespace
from typing import TypedDict, cast, Optional, TYPE_CHECKING, Callable
from os import PathLike
from godocs.cli.command.cli_command import CLICommand
from godocs.cli.command.contruct_command import ConstructCommand
from godocs.plugin import Plugin as PluginType, load as load_plugins
from godocs.util import module

if TYPE_CHECKING:
    from argparse import _SubParsersAction  # type: ignore
    from godocs.cli.command.cli_command import Processor


class AppSubcommands(TypedDict):
    construct: ConstructCommand


class AppCommand(CLICommand):
    """
    The main `CLICommand` for the `godocs` app.

    This command exposes as its main (and only, for now) option the
    `"construct"` subcommand, which triggers the generation of
    documentation output.

    It's possible to extend the functionality of this CLI app
    by providing a path to a script in the `--plugin` or `-p`
    option.
    That script should have a function called `register` with
    its signature expecting an `AppCommand` as its parameter.

    That function can then make any modifications/ additions
    to the application parsers and subparsers as needed.
    """

    parser: ArgumentParser
    """
    The `argparse.ArgumentParser` instance this `AppCommand` uses.
    """

    subparsers: "_SubParsersAction[ArgumentParser]"
    """
    The `subparsers` of the `parser` of this `AppCommand`.
    """

    subcommands: AppSubcommands = {
        "construct": ConstructCommand()
    }
    """
    The subcommands this `AppCommand` exposes.

    Currently, there's only the `"construct"` option.
    """

    processors: list[Callable[[Namespace], Namespace]] = []

    def register(
        self,
        superparsers: "Optional[_SubParsersAction[ArgumentParser]]" = None,
        parent_parser: Optional[ArgumentParser] = None,
        processors: "Optional[list[Processor]]" = None
    ):
        """
        Creates the `parser` for this `AppCommand` and
        registers the `--plugin` or `-p` option, as well
        as sets the help printing function as the default
        behavior when nothing else is chosen.
        """

        self.parser = ArgumentParser(
            description="Godot Docs generator CLI")

        self.parser.set_defaults(execute=self.execute)

        self.subparsers = self.parser.add_subparsers(
            title="command", description="The command to execute.")

        self._register_subcommands()

        plugins = load_plugins()

        for p in plugins:
            self._register_plugin(p)

    def execute(self, args: Namespace):
        self.parser.print_help()

    def parse(self):
        args, _ = self.parser.parse_known_args()

        return args

    def start(self, args: Namespace):
        for processor in self.processors:
            args = processor(args)

        args.execute(args)

    def _register_plugin(self, plugin: str | PathLike[str] | PluginType):
        """
        Executes the registering logic for a `plugin` received, giving
        it this `AppCommand` instance so that it can customize it
        as necessary.
        """

        if not isinstance(plugin, PluginType):
            plugin_module = module.load("plugin", plugin)

            Plugin = dict(
                module.get_classes(plugin_module)).get("Plugin")

            if Plugin is None:
                raise NotImplementedError(
                    f"Plugin {plugin} needs to implement a Plugin class")

            plugin = cast(PluginType, Plugin())

        plugin.register(self)

    def _register_subcommands(self):
        """
        Registers the subcommands for this `AppCommand`.
        """

        # Registers the construct command to the subparsers
        self.subcommands["construct"].register(
            self.subparsers, None, self.processors)
