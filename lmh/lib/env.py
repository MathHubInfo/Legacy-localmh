import os
import sys
import os.path

from lmh.lib.io import std

"""Installation directory of lmh"""
install_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../")

"""Name of the data directory. """
data_dir_name = "MathHub" # TODO: Make this a config

"""Data directory of lmh"""
data_dir = os.path.realpath(os.path.join(install_dir, data_dir_name))

"""External dependencies directory of lmh"""
ext_dir = os.path.realpath(os.path.join(install_dir, "ext"))

def which(program):
    """Returns the full path to program similar to the *nix command which"""
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    # Windows: Maybe its a .exe?
    if os.name == "nt" and not program.endswith(".exe"):
        return which(program+".exe")
    return None

"""sTex directory"""
stexstydir = os.path.join(ext_dir, "sTeX", "sty")

"""LatexML directory"""
latexmlstydir = os.path.join(ext_dir, "LaTeXML", "lib", "LaTeXML", "texmf")
