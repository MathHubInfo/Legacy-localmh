import os
import os.path

from lmh.lib.dirs import lmh_locate
from lmh.lib.io import std, err, write_file, read_file_lines
from lmh.lib.repos.git.install import install

from lmh.lib.repos.local.dirs import match_repos

def export(file = None):
    """Exports the list of currently installed repositories. """

    # Get all locally installed directories
    installed = match_repos(lmh_locate("content"))

    if(file == None):
        for mod in installed:
            std(mod)
        return True
    try:
        write_file(file, os.linesep.join(installed))
        return True
    except:
        err("Unable to write "+file)
        return False

def restore(file = None):
    """Restores a list of currently installed repositories. """

    # read all lines from the file
    lines = read_file_lines(file)
    lines = [l.strip() for l in lines]
    return install(*lines)
