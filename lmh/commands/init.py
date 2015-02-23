from lmh.lib.repos.create import create, find_types

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Initialize repository with MathHub repository structure"
    def add_parser_args(self, parser):
        parser.add_argument('--remote-readonly', '-l', action="store_const", const=True, default=False, help="Do not change anything on the remote (no pushing or creating). ")
        parser.add_argument('name', nargs='?', default=".", help="Name or path of repository to create. Defaults to current directory. ")
        parser.add_argument('--type', '-t', default="none", help="Repository type (one of "+", ".join(find_types())+")")

        parser.epilog = """
    Creates a local MathHub repository and also creates and pushes it to Gitlab.

    Remote repository creation requires access to the Gitlab API. This needs
    either your gitlab username and password or your private token. The private
    token can be configured via

        lmh config gl::private_token <token>

    The private token can be found under Profile -> Account -> Private Token
    on http://gl.mathhub.info.

    If no private token is configured, lmh will automatically ask for your
    username and password.

    To disable any interaction with Gitlab, use the --remote-readonly parameter. """

    def do(self, args, unknown):
        return create(args.name, type=args.type, remote=not args.remote_readonly)
