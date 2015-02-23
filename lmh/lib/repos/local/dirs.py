import os
import os.path
import re
import glob

from lmh.lib.env import install_dir, data_dir
from lmh.lib.io import term_colors, find_files, std, std_paged, err, write_file, read_file, read_file_lines
from lmh.lib.repos import find_dependencies
from lmh.lib.repos.remote import install

from lmh.lib import remove_doubles

# Git imports
from lmh.lib.git import push as git_push
from lmh.lib.git import pull as git_pull
from lmh.lib.git import status_pipe as git_status
from lmh.lib.git import commit as git_commit
from lmh.lib.git import do as git_do
from lmh.lib.git import do_data as git_do_data
from lmh.lib.git import get_remote_status
from lmh.lib.git import is_tracked, is_repo


def is_in_data(path):
    """
        Checks if a directory is contained within the data directory.

        @type path:     string
        @param path:    Path to check

        @rtype:         boolean
    """

    return os.path.abspath(path).startswith(data_dir)

def is_repo_dir(path, existence = True):
    """
        Checks if a directory contains a MathHub repository.

        Optimised to exit as soon as possible when the directory is not
        a repository.

        @param {string} path - Path to check.
        @param {boolean} [existence = true] - Do we do a theoretical test only or do we check for existence as well?

        @returns {boolean}
    """

    #TODO: Check if we need existence.

    # find the relative path
    # by going relatively from the path to the data directory.
    name = os.path.relpath(
        os.path.abspath(path),
        data_dir
    )

    # check if it is indeed a repo name
    # by just counting the number of slashes
    # for this we can omit the last element
    # because it HAS TO BE a letter
    # or is a trailing slash
    slash_num_correct = False
    for c in name[:-1]:
        if c == "/":
            if slash_num_correct:
                # the number is already correct, so it is one
                # and we get to high, so we can abort.
                return False
            # else we found the one and only slash we need
            # and the number is now correct.
            slash_num_correct = True

    # if we need existence, check it is a git directory
    if existence:
        return is_repo(path)

    # we have passed all the tests
    return True

def is_in_repo(path):
    """
        Checks if a directory is contained inside of a repo. Assumes that path
        is a directory.

        If you need to afterwards match a repository name use find_repo_dir
        instead.

        Optimised to exit as soon as possible when path
        is not inside a repository.

        @param {string} path - Path to check.

        @returns {boolean}
    """

    # find the relative path
    # by going relatively from the path to the data directory.
    name = os.path.relpath(
        os.path.abspath(path),
        data_dir
    )

    # Check that the path does not leave the DATA directory.
    # This has to be the first component of the path
    # or the entire path.
    if name.startswith("../") or name == "..":
        return False

    # check if we are inside a repository now
    # for this just match slashes
    for c in name[:-1]:
        if c == "/":
            # we have found a slash, so we are inside.
            return True

    return False

def find_repo_dir(path, existence=True):
    """
        Returns the absolute path to the repository contained in PATH or False.

        If you need to only check if you are in a repository, use is_in_repo
        instead.

        @param {string} path - Path to check
        @param {boolean} [existence = True] - Do we need to check for existence?

        @returns {string|boolean}
    """
    #TODO: Do we need existence.

    # find the relative path
    # by going relatively from the path to the data directory.
    name = os.path.relpath(
        os.path.abspath(path),
        data_dir
    )

    # Check that the path does not leave the DATA directory.
    # This has to be the first component of the path
    # or the entire path.
    if name.startswith("../") or name == "..":
        return False

    # the repository name should be everything until the second slash
    # so go through the path and find it
    num_slash_correct = False
    abs_name = data_dir+"/"
    for (i, c) in enumerate(name):
        if c == "/":
            if num_slash_correct:
                # we have found the second slash
                # we want to check for existence now.
                if existence and not is_repo(abs_name):
                    return False

                # and then return the name.
                return abs_name
            else:
                # we have found the first slash
                num_slash_correct = True
        # add the caracter to the name
        abs_name += c

    # do we have the correct number of slashes?
    # if so, we can return the path.
    if num_slash_correct:
        # again, we might have to check for existence.
        if existence and not is_repo(abs_name):
            return False
        return abs_name
    else:
        return False

def find_repo_subdirs(path):
    """
        Returns the absolute path to the all repositories contained in PATH.

        @param {string} path - Path to check

        @returns {string[]}
    """

    # path needs to be a directory
    if not os.path.isdir(path):
        return []

    # We are not inside the data directory
    # so we need to return nothing
    if not is_in_data(path):
        return []

    # If we can find the current repository path
    # we can return it.
    repo_path = find_repo_dir(path)
    if repo_path:
        return [repo_path]

    # Find the relative path from the root to the current directory
    name = os.path.relpath(
        os.path.abspath(path),
        data_dir
    )

    # make sure everything ends with a slash
    # so that we can count properly
    if name[-1] != "/":
        name += "/"

    # Now figure out which level we are at
    # by counting slashes
    num_slashes = 0
    for c in name:
        # count the slashes
        # by increasing the level.
        if c == "/":
            num_slashes += 1


    # if we have no slashes
    # we are toplevel
    if name == "./":
        name = data_dir+"/*/*"
    # if we have 1 slash
    # we are one level deep
    elif num_slashes == 1:
        name = data_dir+"/"+name+"/*"
    # else something is wrong
    # and we are nowhere
    else:
        return []

    # now we can match the paths via glob.glob
    # and check that they exist
    return filter(is_repo, glob.glob(name))


def match_repo(repo, root=os.getcwd(), abs=False, existence=True):
    """Matches a single specefier to a repository. """

    # 1) Resolve to absolute path repo (via root)
    # 2) If it is (inside) a repository, return that repository
    # 3) If not, try to repeat 1) and 2) with root = data_dir
    # 4) If that fails, return None

    # make sure the root is absolute
    root = os.path.abspath(root)

    # If repo is empty, make sure we use the current directory.
    if repo == "":
        repo = os.getcwd()

    # try the full repo_path
    repo_path = os.path.join(root, repo)

    if is_repo_dir(repo_path, existence) or is_in_repo(repo_path):
        # figure out the path to the repository root
        repo_path = find_repo_dir(repo_path, existence)
        if not repo_path:
            return None
        if abs:
            # return the absolute path to the repo
            return repo_path
        else:
            # return just the repo name, determined by the relative name
            return os.path.relpath(repo_path, os.path.abspath(data_dir))
    elif not (root == os.path.abspath(data_dir)):
        #if the root is not already the data_dir, try that
        return match_repo(repo, root=data_dir, abs=abs,existence=existence)
    else:
        # nothing found
        return None


def match_repos(repos, root=os.getcwd(), abs=False):
    """
        Matches a list of specefiers to repositories.

        @param {string[]} repos - Specefiers to match
        @param {string} root - Root directory to use
        @param {boolean} [abs=False] - Should absolute paths be returned?

        @returns string[] - repository paths
    """

    # For each element do the following:
    # 1) Check if given directory exists relatively from current root.
    #       1a) If it is a repository or repository subdir, return that
    #        1b) If it is inside the data_dir, return all repo subdirectories
    # 2) If it does not exist, resolve it as glob.glob from install_dir
    # 3) For each of the found directories, run 1)

    # If the repositories are just a string, we want an array.
    if isinstance(repos, basestring):
        repos = [repos]
    # it is already an array, so remove doubles please.
    else:
        repos = remove_doubles(repos)

    # the glob expressions we want to use
    # and the repo directories we will use.
    results = set()

    def match_repo_name(r):
        # make an absolute path
        # this will also work with globs
        names = os.path.abspath(os.path.join(root, r))

        # it is not inside the data directory
        # so try again next time
        if not is_in_data(names):
            return True

        # find the relative path of it to the root.
        names = os.path.relpath(
            os.path.abspath(names),
            data_dir
        )

        # make sure everything ends with a slash
        # so that we can count properly
        if names[-1] != "/":
            names += "/"

        # Now figure out which level we are at
        # by counting slashes
        num_slashes = 0
        for c in names:
            # count the slashes
            # by increasing the level.
            if c == "/":
                num_slashes += 1


        # if we have no slashes
        # we are toplevel
        # and can pretty much exit everything
        if names == "./":
            names = data_dir+"/*/*"

        # if we have 1 slash
        # we are one level deep
        elif num_slashes == 1:
            names = data_dir+"/"+names+"*"
        else:
            names = os.path.join(data_dir, names)

        # now expand with the help of globs
        names = glob.glob(names)

        # and check if they exist
        names = filter(is_repo, names)

        # if we found something
        # we should through the item
        if len(names) > 0:
            results.update(names)
            return False
        else:
            return True

    # now filter the repos
    repos = filter(match_repo_name, repos)

    # repeat again with data_dir as root
    root = data_dir
    repos = filter(match_repo_name, repos)


    # if we want the relative paths we need to set them properly.
    if not abs:
        return [os.path.relpath(d, data_dir) for d in results]

    return list(results)
