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

import sys
import argparse

from lmh.lib.env import run_shell

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Shell wrapper. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="shell"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='launch a shell with everything set to run build commands. ')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('shell', nargs="?", help="shell to use")

def do(args):
  code = run_shell(args.shell)
  sys.exit(code)