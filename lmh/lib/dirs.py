"""
Location of directories for built in lmh directories.
"""
import os
import os.path

from lmh.lib.utils import cached

"""Installation directory of lmh"""
install_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../")

"""Name of the library directory of lmh"""
lib_dir_name = "lmh"

"""Name of the data directory"""
data_dir_name = "MathHub"

"""Name of the external directory"""
ext_dir_name = "ext"

@cached
def lmh_locate(*paths):
    """
    Locates a path relative to the localmh install directory. Convenience
    function that wraps os.path.join.

    Additionally this function considers the following special cases for the
    first argument of this function:

    1. "content" the path will be resolved relative to the directory which
        contains content repositories
    2. "ext" the path will be resolved relative to the directory that contains
        external dependencies
    3. "lib" the path will be resolved relative to the lmh directory that contains
        all python source code
    """

    p = list(paths)

    # Rewrite special directories
    if len(p) > 0:
        if p[0] == "content":
            p[0] = data_dir_name
        elif p[0] == "ext":
            p[0] = ext_dir_name
        elif p[0] == "lib":
            p[0] = lib_dir_name

    return os.path.join(install_dir, *p)
