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
