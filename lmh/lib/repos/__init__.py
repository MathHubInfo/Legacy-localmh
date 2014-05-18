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

import re
import argparse
import os.path

from lmh.lib.io import err, read_file_lines
from lmh.lib.git import root_dir
from lmh.lib.env import install_dir, data_dir

"""A regular expression for repository names"""
nameExpression = '[\w-]+/[\w-]+'

def repoType(name):
	"""Repository type for an argument"""
	m = re.match(nameExpression, name)
	if m and len(m.group(0)) == len(name):
		return name
	else:
		raise argparse.ArgumentTypeError("%r is not a valid repository name"%name)

def is_installed(repo):
	"""Checks if a repository is is installed"""

	possible_dir = data_dir + "/" + repo

	return os.path.isdir(possible_dir) and is_valid_repo(possible_dir)

def find_dependencies(repo):
	"""Finds the dependencies of a module. """
	
	if not is_installed(repo):
		err("Repository", repo, "is not installed. Failed to parse dependencies. ")
		return []

	repo = data_dir +"/" + repo

	res = []
	try:
		# Find the root directory
		dir = root_dir(repo)
		metafile = read_file_lines(dir+"/META-INF/MANIFEST.MF")

		# Find the right line for dependencies
		for line in metafile:
			if line.startswith("dependencies: "):
				# TODO: Maybe find a better alternative for this. 
				for dep in re.findall(nameExpression, line):
					res.append(dep)
	except Exception as e:
		return False

	return res

def is_valid_repo(dir):
	"""Validates if dir contains a valid local repository. """

	# TODO: Validate if we have the MANIFEST or a git repository here. 
	# Maybe even somehow generalise install::nodeps

	try:
		return len(dir[len(data_dir)+1:].split("/")) == 2
	except:
		return False
	return True

def is_valid_repo_name(name):
	"""Checks if name is a valid repo name"""
	if name.find("..") != -1:
		return False
	if name == ".":
		return False
	if len(name) == 0:
		return False
	return True

def parseRepo(name):
	"""Turn name into a full repository name"""

	# TODO: un-hardcode the "MathHub" part somehow

	r = repoName.split("/")
	if len(r) == 2 and is_valid_repo_name(r[0]) and is_valid_repo_name(r[1]):
		repoPath = "/".join([data_dir, r[0], r[1]]);
		if os.path.exists(repoPath):
			return repoPath

	fullPath = os.path.normpath(os.path.realpath(repoName))

	if not fullPath.startswith(install_dir):
		raise argparse.ArgumentTypeError("%r is not a valid repository"%fullPath)

	relPath = filter(len, fullPath[len(install_dir)+1:].split(os.sep))

	if len(relPath) == 0 or (len(relPath)==1 and relPath[0]=="MathHub"):
		return data_dir+"/*/*";

	if len(relPath) == 2 and relPath[0]=="MathHub":
		return data_dir+relPath[1]+"/*";

	if len(relPath) > 2:
		return fullPath

	raise argparse.ArgumentTypeError("%r is not a valid repository name"%repoName)

def matchRepo(name, default):
	"""Try and match name to a repository name. If it fails, use the default. """
	try:
		return parseRepo(name)
	except:
		return default