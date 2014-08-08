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

from lmh.lib.io import std, err, read_raw
from lmh.lib.config import get_config
from lmh.lib.repos.remote import install, ls_remote

def create_parser():
    parser = argparse.ArgumentParser(description='Installs MathHub repositories. ')
    add_parser_args(parser)
    return parser

def add_parser(subparsers, name="install"):
    parser_status = subparsers.add_parser(name, help='fetches a MathHub repository and its dependencies')
    add_parser_args(parser_status)

def add_parser_args(parser):
    parser.add_argument('spec', nargs='*', help="A list of repository specs to install. ")
    parser.add_argument('-y', '--no-confirm-install', action="store_true", default=False, help="Do not prompt before installing. ")
    parser.epilog = """
    Use install::sources to configure the sources of repositories.

    Use install::nomanifest to configure what happens to repositories without a manifest.

    Use install::noglobs to disable globbing for lmh install.
    """

def do(args):
    if len(args.spec) == 0:
        err("Nothing to do here ...")
        return True

    if not get_config("install::noglobs"):
        args.spec = ls_remote(*args.spec)
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


    return install(*args.spec)
