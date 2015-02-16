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

import argparse

from lmh.lib import helper
from lmh.lib.repos.create import create, find_types

def add_parser(subparsers, name="init"):
    parser_status = subparsers.add_parser(name, help='initialize repository with MathHub repository structure', formatter_class=helper.LMHFormatter)
    add_parser_args(parser_status)

def add_parser_args(parser):
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

def do(args, unknown_args):
    return create(args.name, type=args.type, remote=not args.remote_readonly)
