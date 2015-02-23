from lmh.lib.io import std, err, read_raw
from lmh.lib.config import get_config
from lmh.lib.repos.remote import install, ls_remote

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Fetch a MathHub repository and its dependencies"
    def add_parser_args(self, parser):
        parser.add_argument('spec', nargs='*', help="A list of repository specs to install. ")
        parser.add_argument('-y', '--no-confirm-install', action="store_true", default=False, help="Do not prompt before installing. ")
        parser.add_argument('-m', '--no-manifest', action="store_true", default=False, help="Do not parse manifest while installing. Equivalent to setting install::nomanifest to True. ")
        parser.epilog = """
    Use install::sources to configure the sources of repositories.

    Use install::nomanifest to configure what happens to repositories without a
    manifest.

    Use install::noglobs to disable globbing for lmh install. """
    def do(self, args, unknown):
        if len(args.spec) == 0:
            err("Nothing to do here ...")
            return True

        if not get_config("install::noglobs"):
            args.spec = ls_remote(args.no_manifest, *args.spec)
            if len(args.spec) == 0:
                err("Nothing to install...")
                return True
            if args.no_confirm_install:
                std("Picked", len(args.spec),"repositories. ")
            else:
                std("Picked", len(args.spec),"repositories: ")
                std(*args.spec)
                if read_raw("Continue (y/N)?").lower() != "y":
                    err("Installation aborted. ")
                    return False


        return install(args.no_manifest, *args.spec)
