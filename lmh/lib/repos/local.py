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
import os.path

from lmh.lib.env import data_dir
from lmh.lib.io import write_file, read_file_lines
from lmh.lib.repos.remote import install
from lmh.lib.repos import is_valid_repo

#
# Matching Repository names
#

def match_repository(dir=os.getcwd()):
	"""Matches a folder to the closest repository. """

	t = os.path.realpath(dir)

	if not t.startswith(data_dir):
		return None

	comp = t[len(data_dir)+1:].split("/")

	if len(comp) < 2:
		return None

	return "/".join(comp[:2])


#
# Local indexers
#

def find_all_locals():
	"""Finds all locally installed repositories"""

	ldirs = []

	# find all sub-sub dirs in the data directory
	for grp in os.listdir(data_dir):
		if os.path.isdir(data_dir + "/" + grp):
			for repo in os.listdir(data_dir + "/" + grp):
				fullPath = data_dir + "/" + grp + "/" + repo
				if os.path.isdir(fullPath) and is_valid_repo(fullPath):
					ldirs.append(grp + "/" + repo)

	return ldirs

#
# Import / Export of all existing repos to a certain file
#

def export(file):

	# Get all locally installed directories
	installed = find_all_locals()

	try:
		write_file(file, s.linesep.join(things))
		return True
	except:
		err("Unable to read "+fn)
		return False

def restore(file):

	# read all lines from the file
	lines = read_file_lines()

	ns = argparse.Namespace()
	ns.__dict__.update({"repository":lines})

	return install.do(ns)