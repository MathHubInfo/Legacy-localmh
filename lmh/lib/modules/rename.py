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
import os.path

from lmh.lib.io import std, err, find_files, read_file, write_file

def rename(where, renamings, simulate = False):
	"""Moves modules from source to dest. """

	where = os.path.abspath(where)

	if not os.path.isdir(where):
		err("Cannot rename:", where, "is not a directory. ")
		return False

	if len(renamings) % 2 != 0:
		err("You must provide renamings in pairs. ")
		return False

	if len(renamings) == 0:
		std("Nothing to rename ...")
		return True

	regexes = []
	replaces = []

	# Compile regexes
	i = 0
	while i< len(renamings):
		find = renamings[i]
		find_parts = find.split("-")
		fl = len(find_parts)
		replace = renamings[i+1]
		replace_parts = replace.split("-")
		rl = len(replace_parts)

		#
		# Defi(i{1, 3})
		#

		if fl > rl:
			# we need fewer stuff => remove some arguments form the end.
			need = fl - rl
			regexes.append(re.compile(r"\\def(?:i{"+str(fl)+r"})\["+find+r"\]((?:\{(?:[^\}])*\}){"+str(rl)+r"})((?:\{(?:[^\}])*\}){"+str(need)+r"})"))
			replaces.append("\\def"+("i"*rl)+"["+replace+"]\\1")
		else:
			need = rl - fl # we need this many more element
			regexes.append(re.compile(r"\\def(?:i{"+str(fl)+r"})\["+find+r"\]"))
			replaces.append("\\def"+("i"*rl)+"["+replace+"]"+("{dummy}"*need))

		# TODO: terfi, atrefi, mtrefi

		# # Trefi
		# regexes.append(re.compile(r"(\\trefi\[[^\]]*\])\{"+find+r"\}"))
		# replaces.append("\\1{"+replace+"}")
		#
		# # Atrefi
		# regexes.append(re.compile(r"(\\atrefi\[[^\]]*\]\{[^\}]*\})\{"+find+r"\}"))
		# replaces.append("\\1{"+replace+"}")
		#
		# # Mtrefi
		# regexes.append(re.compile(r"(\\mtrefi\[([^\?\]]*)\?)"+find+r"\]"))
		# replaces.append("\\1"+replace+"]")
		# # Defii
		# regexes.append(re.compile(r"(\\defii)\["+find[0]+r"\-"+find[1]+r"\]"))
		# replaces.append("\\defii["+replace+"]")
		#
		# #Trefii
		# regexes.append(re.compile(r"(\\trefi\[[^\]]*\])\{"+find[0]+r"\}\{"+find[1]+r"\}"))
		# replaces.append("\\1{"+replace[0]+"}{"+replace[1]+"}")
		#
		# # Atrefii => Not supported, see ticket
		#
		# # Mtrefii
		# regexes.append(re.compile(r"(\\mtrefii\[([^\?\]]*)\?)"+find[0]+r"\-"+find[1]+r"\]"))
		# replaces.append("\\1"+replace[0]+"-"+replace[1]+"]")



		i = i+2

	actions = zip(regexes, replaces)

	# Find all the files
	for file in find_files(where, "tex")[0]:
		# Read a file
		content = read_file(file)

		# Run all of the actions
		for (f, r) in actions:
			content = f.sub(r, content)

		write_file(file, content)

	return True
