from lmh.lib.repos.local.dirs import is_repo_dir, find_repo_dir
from lmh.lib.env import data_dir

from lmh.lib.git import get_remote_status

from lmh.lib.io import read_file_lines
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

    print(package)

    return is_repo_dir(os.path.join(data_dir, package))

def is_upgradable(package):
    """
        Checks if a repository is upgradable.

        @param package {string} Package to check.

        @returns {boolean}
    """

    # If it is not installed, we can not upgrade it.
    if not is_installed(package):
        return False

    # Get the status from the remote repo.
    status = get_remote_status(package)

    # It is upgradable if the remote is newer
    # This is the case if we want to pull.
    return status == "pull"


def get_package_dependencies(package, meta_inf_lines = None):
    """
        Finds package dependencies from a locally installed package.

        @param package {string} Package to check for dependencies.
        @param meta_inf_lines {string[]} Lines in the meta-inf. Optional.

        @returns {string[]}
    """

    if meta_inf_lines == None:
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
            meta_inf_lines = read_file_lines(meta_inf_path)
        except:
            # File is not readable, silently fail.
            return []

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

def build_local_tree(*repos):
    """
        Builds a local dependency tree.

        @param repo {string} - Repository to check.
    """

    # List of repos to be installed.
    repos = list(repos)

    # The dependencies.
    deps = set()

    # The missing items
    missing = set()

    while len(repos) != 0:
        # Pull an element from the list.
        r = repos.pop()[0]

        # If we have it already as a depency
        # or it is missing, skip this iteration
        if r in deps or r in missing:
            continue

        # If it is not installed, it is missing locally
        # and we can not find the dependencies.
        if not is_installed(r):
            missing.add(r)
            continue

        # Add this repository to the depdencies.
        deps.add(r)

        # Find all the local dependencies
        local_deps = get_package_dependencies(r)

        # and add them to the local ones.
        repos.append(local_deps)

    # Return the dependencies
    # and the missing ones as a list
    return (list(deps), list(missing))
