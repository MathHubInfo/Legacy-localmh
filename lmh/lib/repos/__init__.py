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
import os.path

from lmh.lib.io import err, read_file_lines
from lmh.lib.git import root_dir, is_repo
from lmh.lib.env import data_dir

"""A regular expression for repository names"""
nameExpression = '[\w-]+/[\w-]+'

def is_installed(repo):
    """Checks if a repository is is installed"""

    possible_dir = os.path.join(data_dir, repo)

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
        d = root_dir(repo)
        metafile = read_file_lines(os.path.join(d, "META-INF", "MANIFEST.MF"))

        # Find the right line for dependencies
        for line in metafile:
            if line.startswith("dependencies: "):
                # TODO: Maybe find a better alternative for this.
                for dep in re.findall(nameExpression, line):
                    res.append(dep)
    except Exception:
        return False

    return res

def is_valid_repo(d):
    """Validates if dir contains a valid local repository. """
    d = os.path.abspath(d)

    try:
        if not (os.path.relpath(data_dir, os.path.abspath(d)) == "../.."):
            return False
        return is_repo(d)
    except Exception as e:
        err(e)
        return False
