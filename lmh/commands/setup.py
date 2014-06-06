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
from lmh.lib.io import std
import lmh.lib.packs

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Setup tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="setup"):
  parser_status = subparsers.add_parser('setup', formatter_class=argparse.RawTextHelpFormatter, help='sets up local math hub and fetches external requirements')
  add_parser_args(parser_status)

def add_parser_args(parser):
  action = parser.add_argument_group('Setup actions').add_mutually_exclusive_group()

  action.add_argument('--install', action="store_const", dest="saction", const="install", default="", help="Installs a package or group. ")
  action.add_argument('--update', action="store_const", dest="saction", const="update", help="Updates a package or group. ")
  action.add_argument('--reset', '--reinstall', action="store_const", dest="saction", const="reset", help="Resets a package or group. ")
  action.add_argument('--remove', action="store_const", dest="saction", const="remove", help="Removes a package or group. ")

  parser.add_argument('pack', nargs="*", metavar="PACK:SOURCE")

  # Extra Things to install: autocomplete
  #parser.add_argument('--store-source-selections', default=False, const=True, action="store_const", help="If set all source and branch selections are stored and used as default in the future. ", metavar="")

  parser.epilog = """
lmh setup --- Manages extra software required or useful for work with lmh.

Packages are specefied in the format:

PACKAGE_NAME[:SOURCE]

Packages can be installed, updated, removed and reset (reinstalled) via
--install, --update and --reset respectively.

Some packages are installed via git or svn. For those the optional argument
SOURCE specefies which source repository should be used. These can be given in
the format URL[@BRANCH_OR_REVISION]
An example for this is:

lmh setup --install LaTeXML:@dev

which will install the dev branch of LaTeXML.

The following packages are available:

"LaTeXML"        LaTeXML
"LaTeXMLs"       LaTeXML PLugin latexmls
"LaTeXMLStomp"   LaTeXML Plugin latexmlstomp
"sTeX"           sTeX
"MMT"            MMT
"autocomplete"   Automcplete support for lmh. Currently unsupported.
"self"           Meta Package which only supports the update option. Can be used
                 to update lmh.

There are also package groups which simply install several packages at once.
Furthermore, if no packages are given, the "default" package group is used.

The following package groups are available:

"all"            Contains all packages except for the self package.
"default"        Contains LaTeXML, LaTeXMLs, sTeX and MMT.
"LaTeXML-all"    Installs LaTeXML and plugins.
  """

def do(args):
    if len(args.pack) == 0:
        args.pack = ["default"]

    if args.saction == "install":
        return lmh.lib.packs.install(*args.pack)
    elif args.action == "update":
        return lmh.lib.packs.update(*args.pack)
    elif args.action == "remove":
        return lmh.lib.packs.remove(*args.pack)
    elif args.action == "reset":
        return lmh.lib.packs.reset(*args.pack)
    else:
        std("No setup action specefied, assuming --install. ")
        std("Please specify some action in the future. ")
        return lmh.lib.packs.install(*args.pack)
