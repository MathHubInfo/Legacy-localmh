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
import argparse

from lmh.lib import config
from lmh.lib.io import std, err

def create_parser():
	parser = argparse.ArgumentParser(description='Views or changes lmh configuration. ')
	add_parser_args(parser)
	return parser

def add_parser(subparsers, name="config"):
	parser_status = subparsers.add_parser(name, help='Views or changes lmh configuration. ')
	add_parser_args(parser_status)

def add_parser_args(parser):
	parser.add_argument('key', nargs='?', help="Name of setting to change. ", default=None)
	parser.add_argument('value', nargs='?', help="New value for setting. If omitted, show some information about the given setting. ", default=None)
	parser.add_argument('--reset', help="Resets a setting. Ignores value. ", default=False, action="store_const", const=True)
	parser.add_argument('--reset-all', help="Resets all settings. ", default=False, action="store_const", const=True)

def do(args):
	if args.reset_all:
		try:
			os.remove(config.config_file)
			return True
		except:
			pass
		return False

	if args.reset:
		if args.key == None:
			err("Missing key. ")
			return False
		try:
			return config.reset_config(args.key)
		except:
			pass
		return False

	if args.key == None:
		config.list_config()
		std()
		std("Type 'lmh config KEY' to get more information on KEY. ")
		std("Type 'lmh config KEY VALUE' to change KEY to VALUE. ")
		return True
	elif args.value == None:
		return config.get_config_help(args.key)
	else:
		try:
			return config.set_config(args.key, args.value)
		except:
			pass
		return False