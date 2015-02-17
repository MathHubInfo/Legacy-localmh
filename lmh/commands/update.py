"""
This file is part of LMH.

LMH is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LMH is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LMH.  If not, see <http://www.gnu.org/licenses/>.
"""

from lmh.lib.io import std
from lmh.lib.packs import update
from lmh.lib.repos.local import match_repo_args, pull
from lmh.lib.config import get_config
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Get repository and tool updates"
    def add_parser_args(self, parser):
        parser.add_argument('repository', nargs='*', help="a list of repositories which should be updated. ")
        parser.add_argument('--verbose', "-v", default=False, const=True, action="store_const", help="be verbose")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="updates all repositories currently in lmh")
        parser.epilog = """
    If update::selfupdate is set to True, calling lomh update without any arguments
    will also call lmh selfupdate.

    Note: LMH will check for tool updates only if run at the root of the LMH
    folder. """+repo_wildcard_local

    def do(self, args, unknown_args):

        if False and len(args.repository) == 0:
            if get_config("update::selfupdate"):
                std("Selfupdate: ")
                if not update("self"):
                    return False

        repos = match_repo_args(args.repository, args.all)
        return pull(args.verbose, *repos)
