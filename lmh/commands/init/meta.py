def about():
    return "Initialize repository with MathHub repository structure"

def add_parser_args(parser, argparse):
    parser.add_argument('--remote-readonly', '-l', action="store_const", const=True, default=False, help="Do not change anything on the remote (no pushing or creating). ")
    parser.add_argument('name', nargs='?', default=".", help="Name or path of repository to create. Defaults to current directory. ")
    parser.add_argument('--type', '-t', default="none", help="Repository type")

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
