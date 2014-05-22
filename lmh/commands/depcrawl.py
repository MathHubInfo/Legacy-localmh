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

import os
import re
import argparse


from lmh.lib.io import std, err
from lmh.lib.repos.local import calcDeps
from lmh import util

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Path Management tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="depcrawl"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='crawls current repository for dependencies')
  add_parser_args(parser_status)


def add_parser_args(parser):
  parser.add_argument('--apply', metavar='apply', const=True, default=False, action="store_const", help="Option specifying that files should be changed")

def do(rest):
  try:
    std(calcDeps())
    return True
  except Exception as e:
    err(e)
    return False
