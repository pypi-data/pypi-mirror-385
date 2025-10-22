from argparse import ArgumentParser, Namespace
from typing import cast, TYPE_CHECKING, Optional
from godocs.cli.command import CLICommand
from godocs_jinja.constructor import JinjaConstructor
from godocs.constructor.constructor import ConstructorContext

if TYPE_CHECKING:
    from argparse import _SubParsersAction  # type: ignore
    from godocs.cli.command.cli_command import Processor


class JinjaCommand(CLICommand):
    """
    A `CLICommand` that allows defining the behavior of the
    `jinja_constructor`.
    """

    MODELS = ["rst"]
    """
    The default models accepted by this command.
    """

    parser: ArgumentParser
    """
    The `argparse.ArgumentParser` instance this `JinjaCommand` uses.
    """

    subparsers: "_SubParsersAction[ArgumentParser]"
    """
    The `subparsers` of the `parser` of this `AppCommand`.
    """

    def register(
        self,
        superparsers: "Optional[_SubParsersAction[ArgumentParser]]" = None,
        parent_parser: Optional[ArgumentParser] = None,
        processors: "Optional[list[Processor]]" = None
    ):
        """
        Registers this `JinjaCommand` as a subparser for the
        `subparsers` received.
        """

        if superparsers is None:
            raise ValueError('superparsers is needed for "jinja" registration')
        if parent_parser is None:
            raise ValueError(
                'parent_parser is needed for "jinja" registration')

        self.parser: ArgumentParser = superparsers.add_parser(
            "jinja", help="Construct docs using the Jinja constructor.", parents=[parent_parser])

        self.parser.add_argument(
            "-m", "--model",
            default="rst",
            help=f"Which model to use. Can be one of {JinjaCommand.MODELS} or a path to a model directory."
        )
        self.parser.add_argument(
            "-T", "--templates",
            help="Path to directory with Jinja templates."
        )
        self.parser.add_argument(
            "-F", "--filters",
            help="Path to script with Jinja filter functions."
        )
        self.parser.add_argument(
            "-B", "--builders",
            help="Path to script with builders dict."
        )
        self.parser.set_defaults(execute=self.execute)

    def execute(self, args: Namespace):
        """
        Executes the main logic of this command with the parsed `args`.
        """

        constructor = JinjaConstructor(
            model=args.model,
            templates_path=args.templates,
            filters_path=args.filters,
            builders_path=args.builders,
            output_format=args.format,
        )

        constructor.construct(
            cast(ConstructorContext, args.ctx), args.output_dir)
