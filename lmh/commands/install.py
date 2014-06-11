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

from lmh.lib.io import err
from lmh.lib.repos.remote import install

def create_parser():
  parser = argparse.ArgumentParser(description='Installs MathHub repositories. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="install"):
  parser_status = subparsers.add_parser(name, help='fetches a MathHub repository and its dependencies')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', nargs='*', help="a list of remote repositories to fetch locally. Should have form mygroup/myproject. No wildcards allowed. ")
  parser.epilogue = """
  Use install::sources to configure the sources of repositories.
  Use install::nomanifest to configure what happens to repositories without a manifest
  """

def do(args):
  if len(args.repository) == 0:
    err("Nothing to do here ...")
    return True
  return install(*args.repository)
