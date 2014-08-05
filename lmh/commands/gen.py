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

import lmh.lib.modules.generators


from lmh.lib.modules import resolve_pathspec
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

    f = parser.add_argument_group("Generic Options")

    f1 = f.add_mutually_exclusive_group()
    f1.add_argument('-w', '--workers',  metavar='number', default=get_config("gen::default_workers"), type=int, help='Number of worker processes to use. Default determined by gen::default_workers. ')
    f1.add_argument('-s', '--single',  action="store_const", dest="workers", const=1, help='Use only a single process. Shortcut for -w 1')

    f2 = f.add_mutually_exclusive_group()
    f2.add_argument('-n', '--nice', type=int, default=1, help="Assign the worker processes the given niceness. ")
    f2.add_argument('-H', '--high', const=0, dest="nice", action="store_const", help="Generate files using the same priority as the main process. ")

    f3 = f.add_mutually_exclusive_group()
    f3.add_argument('-v', '--verbose', '--simulate', const=True, default=False, action="store_const", help="Dump commands for generation to STDOUT instead of running them. Implies --quiet. ")
    f3.add_argument('-q', '--quiet', const=True, default=False, action="store_const", help="Do not write log messages to STDOUT while generating files. ")

    f4 = parser.add_argument_group("Which files to generate").add_mutually_exclusive_group()
    f4.add_argument('-u', '--update', const="update", default="update", action="store_const", help="Only generate files which have been changed, based on original files. Default. ")
    f4.add_argument('-ul', '--update-log', const="update_log", dest="update", action="store_const", help="Only generate files which have been changed, based on log files. Treated as --force by some generators. ")
    f4.add_argument('-gl', '--grep-log', metavar="PATTERN", dest="grep_log", default=None, help="grep for PATTERN in log files and generate based on those. Treated as --force by some generators. ")
    f4.add_argument('-f', '--force', const="force", dest="update", action="store_const", help="Force to regenerate all files. ")

    whattogen = parser.add_argument_group("What to generate")

    if add_types:
        whattogen.add_argument('--sms', action="store_const", const=True, default=False, help="generate sms files")
        whattogen.add_argument('--omdoc', action="store_const", const=True, default=False, help="generate omdoc files, implies --sms, --alltex, --localpaths")
        whattogen.add_argument('--pdf', action="store_const", const=True, default=False, help="generate pdf files, implies --sms, --alltex, --localpaths")
        whattogen.add_argument('--xhtml', action="store_const", const=True, default=False, help="generate xhtml files, implies --sms, --alltex, --localpaths")
        whattogen.add_argument('--alltex', action="store_const", const=True, default=False, help="Generate all.tex files")
        whattogen.add_argument('--localpaths', action="store_const", const=True, default=False, help="Generate localpaths.tex files")
        whattogen.add_argument('--list', action="store_const", const=True, default=False, help="Lists all modules which exist in the given paths. Blocks all other generation. ")


        parser.add_argument('--pdf-add-begin-document', action="store_const", const=True, default=False, help="add \\begin{document} to LaTeX sources when generating pdfs. Backward compatibility for issue #82")
        parser.add_argument('--pdf-pipe-log', action="store_const", const=True, default=False, help="Displays only the pdf log as output. Implies --quiet, --single")

    whattogen.add_argument('--skip-implies', action="store_const", const=True, default=False, help="Ignore all implications from --omdoc, --pdf and --xhtml. Might cause generation to fail. ")

    wheretogen = parser.add_argument_group("Where to generate")
    wheretogen.add_argument('-d', '--recursion-depth', type=int, default=-1, help="Recursion depth for paths and repositories. ")

    wheretogen = wheretogen.add_mutually_exclusive_group()
    wheretogen.add_argument('pathspec', metavar="PATH_OR_REPOSITORY", nargs='*', default=[], help="A list of paths or repositories to generate things in. ")
    wheretogen.add_argument('--all', "-a", default=False, const=True, action="store_const", help="Generates all files in all repositories. Might take a long time. ")

    return parser

def do(args):
    # If we
    if args.grep_log != None:
        args.update = "grep_log"


    # Make sure we are nice
    if args.nice != 0:
        setnice(args.nice)

    # We should be verbose and run simulate
    if args.verbose:
        args.quiet = True

    # if we are piping pdf log, we need to be quiet and single.
    try:
        if args.pdf_pipe_log:
            args.quiet = True
            args.workers = 1
    except:
        pass

    # When we have nothing to do
    # TODO: Make a joke
    if not args.pdf and not args.omdoc and not args.sms and not args.list and not args.localpaths and not args.alltex and not args.xhtml:
        if not args.quiet:
            std("Nothing to do ...")
        return True

    # Find all the modules
    try:
        if not args.quiet:
            std("Checking modules, this may take a while ...")
        modules = resolve_pathspec(args)
        if not args.quiet:
            std("Found", len(modules), "paths to work on. ")
    except KeyboardInterrupt:
        err("<<KeyboardInterrupt>>")
        return False

    # We want to list all the files
    if args.list:
        for m in modules:
            if m["type"] == "file":
                std(os.path.relpath(m["file"], "."))
        return True

    # Implications to set
    if (args.pdf or args.omdoc or args.xhtml) and not args.skip_implies:
        args.sms = True
        args.localpaths = True
        args.alltex = True

    # SMS Generation
    if args.sms:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.sms, args.grep_log)
        if not args.quiet:
            std("SMS: Generated", len(d), "file(s), failed", len(f), "file(s). ")
        if not res:
            if not args.quiet:
                err("SMS: Generation failed, skipping further generation. ")
            return False


    if args.localpaths and not args.list:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.localpaths, args.grep_log)
        if not args.quiet:
            std("LOCALPATHS: Generated", len(d), "file(s), failed", len(f), "file(s). ")
        if not res:
            if not args.quiet:
                err("LOCALPATHS: Generation failed, skipping further generation. ")
            return False

    if args.alltex and not args.list:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.alltex, args.grep_log)
        if not args.quiet:
            std("ALLTEX: Generated", len(d), "file(s), failed", len(f), "file(s). ")
        if not res:
            if not args.quiet:
                err("ALLTEX: Generation failed, skipping further generation. ")
            return False

    if args.omdoc:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.omdoc, args.grep_log)
        if not args.quiet:
            std("OMDOC: Generated", len(d), "file(s), failed", len(f), "file(s). ")
        if not res:
            if not args.quiet:
                err("OMDOC: Generation failed, skipping further generation. ")
            return False

    if args.pdf:
        if not gen_pdf(modules, args.update == "update", args.verbose, args.quiet, args.workers, args.nice, args.pdf_add_begin_document, args.pdf_pipe_log, args.find_modules):
            if not args.quiet:
                err("PDF: Generation aborted prematurely, skipping further generation. ")
                return False

    if args.xhtml:
        err("XHTML: Not yet implemented. Please use lmh xhtml instead. ")


    return True
