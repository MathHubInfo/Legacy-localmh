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
import sys
import os.path

from lmh.lib.io import std

"""Installation directory of lmh"""
install_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../")

"""Data directory of lmh"""
data_dir = os.path.realpath(install_dir + "/MathHub")

"""Excternale dependencies directory of lmh"""
ext_dir = os.path.realpath(install_dir + "/ext")

def which(program):
	"""Returns the full path to program similar to the *nix command which"""
	def is_exe(fpath):
		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
	
	fpath, fname = os.path.split(program)
	if fpath:
		if is_exe(program):
			return program
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			path = path.strip('"')
			exe_file = os.path.join(path, program)
			if is_exe(exe_file):
				return exe_file

	return None

"""sTex directory"""
stexstydir = install_dir+"/ext/sTeX/sty"

"""LatexML directory"""
latexmlstydir = install_dir+"/ext/sTeX/LaTeXML/lib/LaTeXML/texmf"