import os
import os.path
import re
import glob

from lmh.lib import reduce
from lmh.lib.io import std, err, read_file
from lmh.lib.env import install_dir, data_dir
from lmh.lib.repos.local.dirs import find_repo_dir, find_repo_subdirs

# Hardcoded folder exclude list.
# really ugly workaround for #223
# TODO: Get these files to work.
folder_exclude_list = ["tikz"]


# Hardcoded folder exclude list.
# really ugly workaround for #223
folder_exclude_list = ["tikz"]

def needsPreamble(file):
    """
        Checks if a file needs a preamble.

        @param file File to check.
    """

    # check if we need to add the premable
    return re.search(r"\\begin(\w)*{document}", read_file(file)) == None

def locate_files(path):
    """
        Finds all files matching a specific specification.
        @param path Path to find files in
    """

    # if we are outside data_dir, we return.
    if path.startswith(os.path.abspath(install_dir)) and not path.startswith(os.path.abspath(data_dir)):
        return []

    # fill these modules.
    modules = []

    # Make sure we are inside the source directory.
    if os.path.relpath(data_dir, path) == "../..":
        path = path + "/source"

    # Make it an absolute path.
    path = os.path.abspath(path)


    # if it is a file, we are done.
    if os.path.isfile(path):
        return [path]

    # if it is not a directory, return.
    if not os.path.isdir(path):
        return []

    # find all files and folders.
    objects = [os.path.abspath(path + "/" + f) for f in os.listdir(path)]
    files = filter(lambda f:os.path.isfile(f), objects)
    folders = filter(lambda f:os.path.isdir(f), objects)

    # HACK out the tikz directories.
    folders = filter(lambda f:not f.split("/")[-1] in folder_exclude_list, folders)
    modules = reduce([os.path.abspath(file) for file in files])

    # and go into subdirectories.
    modules.extend(reduce([locate_files(folder) for folder in folders]))

    # return the modules.
    return modules

def locate_compile_target(path, try_root= True):
    """
        Finds all targets to be compiled. (Files AND Folders inside source/)
        @param path Path to find files in
    """
    spec = path

    # if we are not inside the data directory, return.
    if path.startswith(os.path.abspath(install_dir)) and not path.startswith(os.path.abspath(data_dir)):
        # if we have not tried the root, we should try again.
        if try_root:
            return locate_compile_target(os.path.join(data_dir, spec), False)
        return []

    # If we are inside the root, go inside the folder.
    relpath = os.path.relpath(data_dir, os.path.realpath(path))
    if relpath == "../..":
        path = path + "/source"
    elif not relpath.endswith("../.."):
        return reduce([(locate_compile_target(p)) for p in find_repo_subdirs(path)])
    # Get the absolute path.
    path = os.path.realpath(path)

    # If it does not exist, return.
    if not os.path.isfile(path) and not os.path.isdir(path):
        # if we have not tried the root, we should try again.
        if try_root:
            return locate_compile_target(os.path.join(data_dir, spec), False)

        err("Could not find anything matching ", "'"+spec+"'")
        return []

    # find the repository dir.
    repo_dir = find_repo_dir(path, existence=True)
    repo_name = os.path.relpath(repo_dir, data_dir)
    if repo_dir == False:
        # if we have not tried the root, we should try again.
        if try_root:
            return locate_compile_target(os.path.join(data_dir, spec), False)

        err("Matching item to ", "'"+spec+"'", "are outside of repository. ")
        return []

    # Find the source directory and get a relative path
    repos_src_dir = os.path.join(repo_dir, "source")
    path = os.path.relpath(path, repos_src_dir)

    # if we need to go up, we are not in source
    if path.startswith("../"):
        # if we have not tried the root, we should try again.
        if try_root:
            return locate_compile_target(os.path.join(data_dir, spec), False)

        err("Matching item to", "'"+spec+"'", "are outside of the source directory. ")
        return []

    # return the name of the repository and the path inside the repository.
    return [(repo_name, path)]
