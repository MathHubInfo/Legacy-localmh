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

from lmh.lib import setnice
from lmh.lib.io import std, err


from lmh.lib.modules import resolve_pathspec
from lmh.lib.modules.sms import gen_sms
from lmh.lib.modules.localpaths import gen_localpaths
from lmh.lib.modules.alltex import gen_alltex
from lmh.lib.modules.omdoc import gen_omdoc
from lmh.lib.modules.pdf import gen_pdf

from lmh.lib.config import get_config

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Generation tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="gen"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='updates generated content')
  add_parser_args(parser_status)

def add_parser_args(parser, add_types=True):

  flags = parser.add_argument_group("Generation options")

  f1 = flags.add_mutually_exclusive_group()
  f1.add_argument('-w', '--workers',  metavar='number', default=get_config("gen::default_workers"), type=int, help='Number of worker processes to use. Default determined by gen::default_workers. ')
  f1.add_argument('-s', '--single',  action="store_const", dest="workers", const=1, help='Use only a single process. Shortcut for -w 1')

  f2 = flags.add_mutually_exclusive_group()
  f2.add_argument('-u', '--update', const="update", default="update", action="store_const", help="Only generate files which have been changed. DEFAULT. ")
  f2.add_argument('-ul', '--update-log', const="update_log", dest="update", action="store_const", help="Only generate files which have been changed, based on log files. Treated as -u for sms files. UNIMPLEMENTED and currently trated as --force. ")
  f2.add_argument('-f', '--force', const="force", dest="update", action="store_const", help="Force to regenerate all files. ")

  f3 = flags.add_mutually_exclusive_group()
  f3.add_argument('-n', '--nice', type=int, default=1, help="Assign the worker processes the given niceness. ")
  f3.add_argument('-H', '--high', const=0, dest="nice", action="store_const", help="Generate files using the same priority as the main process. ")

  f4 = flags.add_mutually_exclusive_group()
  f4.add_argument('-v', '--verbose', '--simulate', const=True, default=False, action="store_const", help="Dump commands for generation to STDOUT instead of running them. Implies --quiet. ")
  f4.add_argument('-q', '--quiet', const=True, default=False, action="store_const", help="Do not write log messages to STDOUT while generating files. ")
  f4.add_argument('-m', '--find-modules', const=True, default=False, action="store_const", help="Find modules to generate and dump them to STDOUT. Implies --skip-implies, --quiet. Incompatible with --localpaths and --alltex. ")

  whattogen = parser.add_argument_group("What to generate")

  if add_types:

    whattogen.add_argument('--sms', action="store_const", const=True, default=False, help="generate sms files")
    whattogen.add_argument('--omdoc', action="store_const", const=True, default=False, help="generate omdoc files, implies --sms, --alltex, --localpaths")
    whattogen.add_argument('--pdf', action="store_const", const=True, default=False, help="generate pdf files, implies --sms, --alltex, --localpaths")

    whattogen.add_argument('--alltex', action="store_const", const=True, default=False, help="Generate all.tex files")
    whattogen.add_argument('--localpaths', action="store_const", const=True, default=False, help="Generate localpaths.tex files")

    whattogen.add_argument('--list', action="store_const", const=True, default=False, help="Lists all modules which exist in the given paths. If enabled, --sms --omdoc and --pdf are ignored. ")


    parser.add_argument('--pdf-add-begin-document', action="store_const", const=True, default=False, help="add \\begin{document} to LaTeX sources when generating pdfs. Backward compatibility for issue #82")
    parser.add_argument('--pdf-pipe-log', action="store_const", const=True, default=False, help="Displays only the pdf log as output. Implies --quiet, --single")


  whattogen.add_argument('--skip-implies', action="store_const", const=True, default=False, help="Generate only what is requested explicitly. Might fail if some files are missing. ")

  wheretogen = parser.add_argument_group("Where to generate")
  wheretogen.add_argument('-d', '--recursion-depth', type=int, default=-1, help="Recursion depth for paths and repositories. ")

  wheretogen = wheretogen.add_mutually_exclusive_group()
  wheretogen.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to generate things in. ")
  wheretogen.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")

  return parser

def do(args):
  if args.nice != 0:
    # set niceness
    setnice(args.nice)

  if args.verbose:
    args.quiet = True

  try:
    if args.pdf_pipe_log:
      args.quiet = True
      args.workers = 1
  except:
    pass

  if args.find_modules:
    args.skip_implies = True
    args.quiet = True

  if not args.pdf and not args.omdoc and not args.sms and not args.list and not args.localpaths and not args.alltex:
    if not args.quiet:
      std("Nothing to do ...")
    return True

  # Find all the modules
  try:
    if not args.quiet:
      std("Checking modules ...")
    modules = resolve_pathspec(args)
    if not args.quiet:
      std("Found", len(modules), "paths to work on. ")
  except KeyboardInterrupt:
    err("<<KeyboardInterrupt>>")
    return False

  # if we just need to list modules
  if args.list:
    for m in modules:
      if m["type"] == "file":
        std("./"+os.path.relpath(m["file"], "./"))
    return True

  # Check what we need to do
  if (args.pdf or args.om doc) and not args.skip_implies:
    args.sms = True
    args.localpaths = True
    args.alltex = True

  if args.sms:
    if not gen_sms(modules, args.update, args.verbose, args.quiet, args.workers, args.nice, args.find_modules):
      if not args.quiet:
        err("SMS: Generation aborted prematurely, skipping further generation. ")
      return False

  if args.localpaths and not args.find_modules:
    if not gen_localpaths(modules, args.update == "update", args.verbose, args.quiet, args.workers, args.nice):
      if not args.quiet:
        err("LOCALPATHS: Generation aborted prematurely, skipping further generation. ")
      return False

  if args.alltex and not args.find_modules:
    if not gen_alltex(modules, args.update == "update", args.verbose, args.quiet, args.workers, args.nice):
      if not args.quiet:
        err("ALLTEX: Generation aborted prematurely, skipping further generation. ")
      return False

  if args.omdoc:
    if not gen_omdoc(modules, args.update == "update", args.verbose, args.quiet, args.workers, args.nice, args.find_modules):
      if not args.quiet:
        err("OMDOC: Generation aborted prematurely, skipping further generation. ")
      return False

  if args.pdf:
    if not gen_pdf(modules, args.update == "update", args.verbose, args.quiet, args.workers, args.nice, args.pdf_add_begin_document, args.pdf_pipe_log, args.find_modules):
      if not args.quiet:
        err("PDF: Generation aborted prematurely, skipping further generation. ")
      return False

  return True
