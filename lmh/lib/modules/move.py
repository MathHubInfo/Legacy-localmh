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
import sys
import glob
import json
import shutil

from lmh.lib import reduce
from lmh.lib.io import find_files, std, err
from lmh.lib.env import data_dir

from lmh.lib.repos.local import match_repos
from lmh.lib.repos.find_and_replace import find_cached

def movemod(source, dest, modules, simulate = False):
	"""Moves modules from source to dest. """

	# change directory to MathHub root, makes paths easier
	if simulate:
		std("cd "+data_dir)
	else:
		os.chdir(data_dir)

	finds = []
	replaces = []

	odest = dest

	# Make a list of all the moved files.
	moved_files = []

	local_finds = []
	local_replaces = []

	def run_lmh_find_moved(find, replace):
		if simulate:
			# We will run it over dest only.
			std("lmh", "find", json.dumps(find), "--replace", json.dumps(replace), "--apply", odest)
		else:
			# Append it to to a list.
			local_finds.append(find)
			local_replaces.append(replace)

	for module in modules:

		dest = odest

		# Figure out the full path to the source
		srcpath = source + "/source/" +  module

		# Assemble source paths further
		srcargs = (source + "/" + module).split("/")
		srcapath = "\\/".join(srcargs[:-1])
		srcbpath = srcargs[-1]

		# Assemble all the commands
		oldcall = "\[" + srcapath + "\]\{"+srcbpath+"\}"
		oldcall_long = "\[(.*)repos=" + srcapath + "(.*)\]\{"+srcbpath+"\}"
		oldcall_local = "\{"+srcbpath+ "\}"
		newcall = "[" + dest + "]{"+srcbpath+"}"
		newcall_long = "[$g1" + dest + "$g2]{"+srcbpath+"}"

		dest += "/source/"

		# Move the files
		if simulate:
			std("mv "+srcpath + ".*.tex"+ " "+ dest + " 2>/dev/null || true")
			std("mv "+srcpath + ".tex"+ " "+ dest + " 2>/dev/null || true")
		else:
			try:
				shutil.move(srcpath + ".tex", dest)
				moved_files.append(os.path.join(dest, os.path.basename(srcpath + ".tex")))
			except:
				pass

			for pat in glob.glob(srcpath + ".*.tex"):
				# try to move the file if it exists
				try:
					shutil.move(pat, dest)
					moved_files.append(os.path.join(dest, os.path.basename(pat)))
				except:
					pass


		def run_lmh_find(find, replace):
			finds.append(find)
			replaces.append(replace)

		# Run all the commands
		m = "("+"|".join(["gimport", "guse", "gadopt"])+")"
		run_lmh_find(r'\\'+m+oldcall, '\\$g0'+newcall)
		run_lmh_find(r'\\'+m+oldcall_local, '\\$g0'+newcall)

		m = "("+ "|".join(["importmhmodule", "usemhmodule", "adoptmhmodule", "usemhvocab"]) + ")"
		run_lmh_find(r'\\'+m+oldcall_long, '\\$g0'+newcall_long)
		run_lmh_find(r'\\'+m+oldcall_local, '\\$g0'+newcall_long)

		# For the moved files, repalce gimport, guse, gadpot 
		run_lmh_find_moved(r"\\("+"|".join(["gimport", "guse", "gadopt"])+")\["+dest[-len("/source/")]+"\]\{(.*)\}", "\\$g1{$g2}")

	# Update the moved files.
	run_lmh_find_moved(r"\\("+"|".join(["gimport", "guse", "gadopt"])+")\{(((?!(?<=\{)("+modules.join("|")+")\}).)*?)\}", "\\$g1{$g2}")



	files = reduce([find_files(r, "tex")[0] for r in match_repos(data_dir, abs=True)])

	if simulate:
		for (f, r) in zip(finds, replaces):
			std("lmh find", json.dumps(f), "--replace", json.dumps(r), "--apply")
	else:
		std("updating paths in the following files: ")

		res1 = find_cached(files, finds, replace=replaces)
		res2 = find_cached(moved_files, local_finds, replace=local_replaces)

		return res1 and res2
