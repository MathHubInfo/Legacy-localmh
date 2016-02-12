from lmh.lib.repos.local.dirs import is_repo_dir, find_repo_dir
from lmh.lib.dirs import lmh_locate

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

    return is_repo_dir(lmh_locate("content", package))

def get_metainf_lines(package):
    """
        Gets the lines of the meta-inf file.

        @param package {string} Package to read meta-inf lines form.

        @returns {string[]}
    """

    # Find the package root directory.
    package_dir = find_repo_dir(lmh_locate("content", package))

    # Check that repository is installed.
    if not package_dir:
        err("Repository", package, "is not installed. Failed to read META-INF. ")
        return []

    # Read the path to meta_inf
    meta_inf_path = os.path.join(package_dir, "META-INF", "MANIFEST.MF")

    try:
        # Try and read the file lines
        return read_file_lines(meta_inf_path)
    except:
        # File is not readable, silently fail.
        return []

def get_package_id(package):
    """
        Reads the id of a locally installed package.

        @param package {string} Package to find id of.

        @returns {string}
    """

    # Read the meta-inf lines.
    meta_inf_lines = get_metainf_lines(package)

    # Prefix for name
    id_prefix = "id:"

    # go through each of the lines
    for line in meta_inf_lines:
        if line.startswith(id_prefix):
            # cut off the beginning and remove spaces.
            return line[len(id_prefix):].strip()

    # return just the name if we did not find a line.
    return name

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
            line = whiteSpaceExpression.sub(" ", line).strip()

            # and update the dependencies
            dependencies.update(line.replace(" ", ",").split(","))

    # return a list of them
    return list(filter(lambda x:x, [d.strip() for d in dependencies]))
