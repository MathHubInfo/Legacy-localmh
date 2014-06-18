#!/usr/bin/env python
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

from lmh.commands.gen import add_parser_args

def create_parser(submods = {}):

	#
	# The main parser
	#
	parser = argparse.ArgumentParser(description='Local MathHub Tool.')

	parser.add_argument("-q", "--quiet", action="store_true", default=False, help="Disables any output to stdout and stderr. ")
	parser.add_argument("--non-interactive", "-ni",  action="store_true", default=False, help="Disables interactivity (prompts from stdin) and causes lmh to abort in those cases. ")

	#
	# Subcommands
	#

	subparsers = parser.add_subparsers(help='valid actions are:', dest="action", metavar='action')


	#
	# Group and load submodules
	#

	submodules = [
		"init", "status", "install", "commit", "push", "update", "git", "log", "mine", "ls",

		"about", "setup", "config", "selfupdate", "issue", "ls-remote",

		"gen", "update-build", "clean", "xhtml", "shell",

		"find", "depcrawl", "checkpaths", "mvmod", "symbols"
	]

	for mod in submodules:
		_mod = getattr(getattr(__import__("lmh.commands."+mod), "commands"), mod)
		submods[mod] = _mod
		_mod.add_parser(subparsers)

	#
	# Command aliases
	#

	aliases = {
		"commit": "ci",
		"update": "up",
		"status": "st"
	}

	for cmd in aliases:
		mod = aliases[cmd]
		_mod = getattr(getattr(__import__("lmh.commands."+cmd), "commands"), cmd)
		submods[mod] = _mod
		_mod.add_parser(subparsers, mod)

	#
	# Special commands, directly implemented.
	# TODO: Port all of these to seperate files
	#

	subparsers.add_parser('root', help='prints the root directory of the Local Math Hub repository')

	add_parser_args(subparsers.add_parser('sms', help='generates sms files, alias for lmh gen --sms'), add_types=False).epilog = "Generate sms files. "
	add_parser_args(subparsers.add_parser('omdoc', help='generates omdoc files, alias for lmh gen --omdoc'), add_types=False).epilog = "Generate omdoc files. "

	p = add_parser_args(subparsers.add_parser('pdf', help='generates pdf files, alias for lmh gen --pdf'), add_types=False)
	p.add_argument('--pdf-add-begin-document', action="store_const", const=True, default=False, help="add \\begin{document} to LaTeX sources when generating pdfs. Backward compatibility for issue #82")
	p.add_argument('--pdf-pipe-log', action="store_const", const=True, default=False, help="Displays only the pdf log as output. Implies --quiet. ")
	p.epilog = "Generate pdf files. "

	return parser
