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

def create_parser(submods = {}):
	parser = argparse.ArgumentParser(description='Local MathHub XHTML conversion tool.')
	reps = [];

	subparsers = parser.add_subparsers(help='valid actions are:', dest="action", metavar='action')

	submodules = ["about", "find", "status", "log", "install", "setup", "xhtml", "init", "commit", "push", "update", "gen", "clean", "git", "depcrawl", "checkpaths"];
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

	reps.append(subparsers.add_parser('sms', help='generates sms files'))
	reps.append(subparsers.add_parser('omdoc', help='generates omdoc for targets'))
	reps.append(subparsers.add_parser('pdf', help='generates pdf for targets, short form for lmh gen --pdf'))
	reps.append(subparsers.add_parser('mods', help='generates omdoc module files'))
	reps.append(subparsers.add_parser('modspdf', help='generates omdoc module files, short form for lmh gen --omdoc'))


	for rep in reps:
		rep.add_argument('repository', type=util.parseRepo, nargs='*', help="a list of repositories. ").completer = util.autocomplete_mathhub_repository
		rep.add_argument('repository', type=util.parseRepo, nargs='*', help="a list of repositories. ").completer = util.autocomplete_mathhub_repository
		rep.add_argument('-f', '--force', const=True, default=False, action="store_const", help="force all regeneration")


	if util.module_exists("argcomplete"):
		__import__("argcomplete").autocomplete(parser)

	return parser