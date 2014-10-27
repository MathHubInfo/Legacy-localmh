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
from lmh.lib.modules.translate import transmod

def create_parser():
    parser = argparse.ArgumentParser(description='Translates an existing multilingual module to a new language. ')
    add_parser_args(parser)
    return parser

def add_parser(subparsers, name="translate"):
    parser_status = subparsers.add_parser(name, help='Translates an existing multilingual module to a new language. ')
    add_parser_args(parser_status)

def add_parser_args(parser):
    parser.add_argument('--force', action="store_true", default=False, help="Overwrite existing modules. ")
    parser.add_argument('source', nargs=1, help="Name of the existing language. ")
    parser.add_argument('dest', nargs="+", help="Name(s) of the new language(s). ")
    parser.add_argument('--terms', default=None, help="Terms to pre-translate. Either a Path to a json file or a JSON-encoded string. ")

    parser.epilog = """
    Example: lmh translate functions.en.tex de

    Which translates the english version functions.en.tex to a new german version
    which will be called functions.de.tex.

    The terms argument should have the following structure:

    {
        "source_language": {
            "target_language": {
                "word": "translation"
            }
        }
    }

    Will require manual completion of the translation.
    """

def do(args):
    ret = True

    multiregex = r"(.*)\.(.*)\.tex"

    args.source = args.source[0]

    try:
        ofn = os.path.abspath(args.source)
        ofn = re.findall(multiregex, ofn)[0]
    except:
        err("Module", args.source, "does not seem to be multi-lingual. ")
        err("(Can not extract language from filename. )")
        err("Please rename it to <module>.<language>.tex and try again. ")
        return False

    if not os.path.isfile(os.path.abspath(args.source)):
        err("File", args.source, " does not exist. ")
        return False

    for lang in args.dest:
        langfn = ofn[0]+"."+lang+".tex"
        if not args.force and os.path.isfile(langfn):
            err("File", langfn, "exists, skipping. ")
            err("Use --force to overwrite. ")
            ret = False
            continue

        ret = transmod(ofn[0], ofn[1], lang, pre_terms = args.terms) and ret

    return ret
