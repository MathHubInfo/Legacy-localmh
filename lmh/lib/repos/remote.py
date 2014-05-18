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

from lmh.lib.io import std, err
from lmh.lib.env import data_dir
from lmh.lib.git import clone, exists
from lmh.lib.repos import is_installed, find_dependencies
from lmh.lib.config import get_config

def find_source(name):
	"""Finds the source of a repository. """

	root_urls = get_config("install::sources").rsplit(";")
	root_suffix = ["", ".git"]
	for i in range(len(root_urls)):
		url = root_urls[i]
		url_suf = root_suffix[i]
		if exists(url+name+url_suf):
			return url+name+url_suf

	err("Can not find remote repository", name)
	err("Please check install::sources and check your network connection. ")
	return False

#
# Installing a repository
#

def force_install(rep):
	"""Forces installation of a repository"""
	std("Installing", rep)

	# Find the source for the repository
	repoURL = find_source(rep)

	if repoURL == False:
		return False

	# Clone the repo
	return clone(data_dir, repoURL, rep)


def install(*reps):
	"""Install a repositories and its dependencies"""

	reps = [r for r in reps]

	for rep in reps:
		if not is_installed(rep):
			if not force_install(rep):
				err("Unable to install", rep)
				return False

		try:
			std("Resolving dependencies for", rep)
			for dep in find_dependencies(rep):
				if not (dep in reps) and not is_installed(dep):
					std("Found unsatisfied dependency:", dep) 
					reps.append(dep)
		except:
			if not get_config("install::nomanifest"):
				err("Error parsing dependencies for", rep)
				err("Set install::nomanifest to True to disable this. ")
				return False