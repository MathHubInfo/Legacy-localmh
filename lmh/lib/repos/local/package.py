from lmh.lib.repos.local.dirs import is_repo_dir, find_repo_dir
from lmh.lib.env import data_dir

from lmh.lib.io import err, read_file_lines
import os.path

import re

"""Regular expression for replaceing whitespaces. """
whiteSpaceExpression=re.compile(r"\s+")

def is_installed(package):
    """
        Checks if a repository is installed locally.

        @param package {string} Package to check.

        @returns {boolean}
    """

    return is_repo_dir(os.path.join(data_dir, package))

def get_metainf_lines(package):
    """
        Gets the lines of the meta-inf file. 

        @param package {string} Package to read meta-inf lines form.

        @returns {string[]}
    """

    # Find the package root directory.
    package_dir = find_repo_dir(os.path.join(data_dir, package))

    # Check that repository is installed.
    if not package_dir:
        err("Repository", package, "is not installed. Failed to parse dependencies. ")
        return []

    # Read the path to meta_inf
    meta_inf_path = os.path.join(package_dir, "META-INF", "MANIFEST.MF")

    try:
        # Try and read the file lines
        return read_file_lines(meta_inf_path)
    except:
        # File is not readable, silently fail.
        return []

def get_package_dependencies(package):
    """
        Finds package dependencies from a locally installed package.

        @param package {string} Package to check for dependencies.

        @returns {string[]}
    """

    # Read the meta-inf lines.
    meta_inf_lines = get_metainf_lines(package)

    # Dependencies we want to have
    dependencies = set()

    deps_prefix = "dependencies: "
    # go through each of the lines
    for line in meta_inf_lines:
        if line.startswith(deps_prefix):
            # cut off the beginning and replace spaces.
            line = line[len(deps_prefix):]
            line = whiteSpaceExpression.sub("", line)

            # and update the dependencies
            dependencies.update(line.split(","))

    # return a list of them
    return list(dependencies)