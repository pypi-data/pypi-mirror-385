from godocs.plugin import Plugin as BasePlugin
from godocs.cli import AppCommand
from godocs_jinja.cli.command import JinjaCommand


class JinjaPlugin(BasePlugin):

    def register(self, app: AppCommand):
        construct = app.subcommands['construct']

        construct.subcommands["jinja"] = JinjaCommand()

        construct.subcommands["jinja"].register(
            construct.subparsers,
            construct.parent_parser
        )
