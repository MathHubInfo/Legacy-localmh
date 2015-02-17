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
from lmh.lib.repos.local import match_repo_args
from lmh.lib.help import repo_wildcard_local

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="List installed repositories"
    def add_parser_args(self, parser):
        parser.add_argument('repository', nargs='*', help="list of repository specefiers. ")
        parser.add_argument('--abs', '-A', default=False, action="store_true", help="Print absolute repository paths. ")
        parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="list all repositories")
        parser.epilog = repo_wildcard_local
    def do(self, args, unknown_args):
        repos = match_repo_args(args.repository, args.all, abs=args.abs)
        for r in repos:
            std(r)
        return True
