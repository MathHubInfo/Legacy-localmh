#!/usr/bin/env python

"""
Local Math Hub utility main parser. 

.. argparse::
   :module: lmh
   :func: create_parser
   :prog: lmh

"""

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
from lmh import util
from lmh.commands.gen import add_parser_args

def create_parser(submods = {}):
	parser = argparse.ArgumentParser(description='Local MathHub XHTML conversion tool.')
	reps = [];

	subparsers = parser.add_subparsers(help='valid actions are:', dest="action", metavar='action')

	submodules = ["config", "about", "find", "status", "log", "install", "setup", "shell", "xhtml", "init", "commit", "push", "update", "selfupdate", "gen", "clean", "git", "depcrawl", "checkpaths"];
	for mod in submodules:
		_mod = getattr(getattr(__import__("lmh.commands."+mod), "commands"), mod)
		submods[mod] = _mod
		_mod.add_parser(subparsers)	

	# Define command aliases here. 
	aliases = {
		"commit": "ci", 
		"update": "up", 
		"status": "st"
	}

	for cmd in aliases:
		# Makes an alias
		mod = aliases[cmd]
		_mod = getattr(getattr(__import__("lmh.commands."+cmd), "commands"), cmd)
		submods[mod] = _mod
		_mod.add_parser(subparsers, mod)

	# Sepcial commands
	subparsers.add_parser('repos', help='prints the group/repository of the current  Math Hub repository')
	subparsers.add_parser('root', help='prints the root directory of the Local Math Hub repository')

	add_parser_args(subparsers.add_parser('sms', help='generates sms files, alias for lmh gen --sms'), add_types=False).epilog = "Generate sms files. "
	add_parser_args(subparsers.add_parser('omdoc', help='generates omdoc files, alias for lmh gen --omdoc'), add_types=False).epilog = "Generate omdoc files. "
	
	p = add_parser_args(subparsers.add_parser('pdf', help='generates pdf files, alias for lmh gen --pdf'), add_types=False)
	p.add_argument('--pdf-add-begin-document', action="store_const", const=True, default=False, help="add \\begin{document} to LaTeX sources when generating pdfs. Backward compatibility for issue #82")
	p.add_argument('--pdf-pipe-log', action="store_const", const=True, default=False, help="Displays only the pdf log as output. Implies --quiet. ")

	p.epilog = "Generate pdf files. "

	if util.module_exists("argcomplete"):
		__import__("argcomplete").autocomplete(parser)

	return parser

def preparse_args(args):
	#if args[0] == "git":
	#   args = ["git"] + map(lambda a: "\""+"\"", args[1:])
	return args