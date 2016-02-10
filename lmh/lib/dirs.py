"""
Location of directories for built in lmh directories.
"""
import os
import os.path

from lmh.lib.utils import cached

"""Installation directory of lmh"""
install_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../")

"""Library directory of lmh"""
lib_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../")

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

    1. "content" the path will be resolved relative to the data_dir
    2. "ext" the path will be resolved relative to the ext_dir
    3. "lib" the path will be resolved relative to the main lmh module directory
    """

    if len(paths) > 0:
        if paths[0] == "content":
            return os.path.join(install_dir, data_dir_name, *paths[1:])
        if paths[0] == "ext":
            return os.path.join(install_dir, ext_dir_name, *paths[1:])
        if paths[0] == "lib":
            return os.path.join(lib_dir, *paths[1:])

    return os.path.join(install_dir, *paths)

"""Data directory of lmh"""
data_dir = lmh_locate("content")

"""External dependencies directory of lmh"""
ext_dir = lmh_locate("ext")
