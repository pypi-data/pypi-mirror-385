from argparse import ArgumentParser, Namespace
from typing import Optional, TYPE_CHECKING
from godocs.cli.command.cli_command import CLICommand
from godocs.parser import xml_parser, context_creator
from godocs.translation.interpreter import BBCodeInterpreter
from godocs.translation.translator import get_translator
from godocs import util

if TYPE_CHECKING:
    from argparse import _SubParsersAction  # type: ignore
    from godocs.cli.command.cli_command import Processor


class ConstructCommand(CLICommand):
    """
    A `CLICommand` that allows choosing a `constructor` for
    generating documentation.
    """

    TRANSLATORS = ["rst"]
    """
    The default translators accepted by this command.
    """

    parser: ArgumentParser
    """
    The `argparse.ArgumentParser` instance this `ConstructCommand` uses.
    """

    subparsers: "_SubParsersAction[ArgumentParser]"
    """
    The `subparsers` of the `parser` of this `ConstructCommand`.
    """

    parent_parser: ArgumentParser = ArgumentParser(add_help=False)
    """
    An `ArgumentParser` that holds common parameters and options for all
    the constructor types chosen.
    """

    subcommands: dict[str, CLICommand] = {}
    """
    The subcommands this `ConstructCommand` exposes.
    """

    def register(
        self,
        superparsers: "Optional[_SubParsersAction[ArgumentParser]]" = None,
        parent_parser: Optional[ArgumentParser] = None,
        processors: "Optional[list[Processor]]" = None
    ):
        """
        Registers this `ConstructCommand` as a subparser for the
        `subparsers` received.
        """

        if superparsers is None:
            raise ValueError(
                'superparsers are needed for "construct" registration')
        if processors is None:
            raise ValueError(
                'processors are needed for "construct" registration')

        self.parser = superparsers.add_parser(
            "construct", help="Construct documentation with a chosen backend")

        self.parent_parser.add_argument(
            "-t", "--translator",
            default="rst",
            help=f"Which translator to use. Can be one of {self.TRANSLATORS} or a path to a script."
        )
        self.parent_parser.add_argument(
            "-f", "--format",
            default="rst",
            help=f"Which file format suffix to use on generated documentation."
        )
        self.parent_parser.add_argument(
            "-O", "--options-file",
            help=f"Path to options JSON with data to use in documentation."
        )
        self.parent_parser.add_argument(
            "input_dir", help="Input directory with XML documentation files."
        )
        self.parent_parser.add_argument(
            "output_dir", help="Output directory to save generated documentation."
        )

        processors.append(self.process)

        self.parser.set_defaults(execute=self.execute)

        self.subparsers = self.parser.add_subparsers(
            title="constructor", dest="constructor", description="The constructor to use.")

    def execute(self, args: Namespace):
        self.parser.print_help()

    def process(self, args: Namespace):
        if not hasattr(args, "input_dir") or not hasattr(args, "output_dir"):
            return args

        docs = xml_parser.parse(args.input_dir)

        options: dict[str, str] = {}

        if args.options_file != None:
            options = util.options.load(args.options_file)

        ctx = context_creator.create(docs, options)

        interpreter = BBCodeInterpreter()

        translator = get_translator(args.translator)

        ctx = context_creator.translate(ctx, interpreter, translator)

        args.ctx = ctx

        return args
