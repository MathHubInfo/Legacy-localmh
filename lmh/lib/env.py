"""
Location and Helper functions for dependencies of lmh. 
"""
import os.path
import sys

from lmh.lib.io import is_string
from lmh.lib.io import std, err, read_file
from lmh.lib.dirs import lmh_locate, install_dir
from lmh.lib.config import get_config

from subprocess import Popen

import shlex

try:
    import signal
except:
    pass

"""sty directory"""
stydir = lmh_locate("sty")

"""sTex directory"""
stexstydir = lmh_locate("ext", "sTeX", "sty")

"""LatexML directory"""
latexmlstydir = lmh_locate("ext", "LaTeXML", "lib", "LaTeXML", "texmf")

def which(program):
    """
    Returns the full path to a program that can be found in the users $PATH 
    variable. Similar to the *nix command which (or the windows command where). 
    """
    
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


"""Path to the latexmlc executable"""
latexmlc_executable = get_config("env::latexmlc")
latexmlc_builtin = False

# Find it the old way if not available
if latexmlc_executable == "":    
    latexmlc_executable = which("latexmlc")

"""Path to the git executable """
git_executable = get_config("env::git")

# Find it yourself if the config is empty
if git_executable == "":
    git_executable = which("git")

"""Path to the pdflatex executable. """
pdflatex_executable = get_config("env::pdflatex")

if pdflatex_executable == "":
    pdflatex_executable =  which("xelatex")

"""Path to the perl executable. """
perl_executable = get_config("env::perl")

if perl_executable == "":
    perl_executable =  which("perl")

"""Path to the MMT executable. """
mmt_executable = get_config("env::mmt")

if mmt_executable == "":
    mmt_executable = install_dir+"/ext/MMT/deploy/mmt.jar"

"""Path to the cpanm executable. """
cpanm_executable = get_config("env::cpanm")

if cpanm_executable == "":
    cpanm_executable = which("cpanm")

"""Path to the cpanm executable. """
wget_executable = get_config("env::wget")

if wget_executable == "":
    wget_executable = which("wget")

def run_shell(shell = None, args=""):
    """
    Runs a shell in which all external programs can run
    """

    # If args is a list, join it by " "s
    if not is_string(args):
        args = " ".join(args)


    if shell == None:
        try:
            shell = os.environ["SHELL"] or which("bash")
        except:
            shell = which("bash")

            if shell == None:
                err("Unable to find bash shell, please provide another one. ")
                return 127
    else:
        shell = which(shell)
        if shell == None:
            return 127

    # Make a perl 5 environment
    _env = os.environ.copy()
    _env["STEXSTYDIR"] = stexstydir

    # pdf inputs
    def genTEXInputs():
        res = ".:"+stydir+":";
        for (root, files, dirs) in os.walk(stexstydir):
            res += root+":"
        for (root, files, dirs) in os.walk(latexmlstydir):
            res += root+":"
        return res+":"+latexmlstydir+":"+stexstydir

    _env["TEXINPUTS"] = genTEXInputs()
    _env["PATH"] = stexstydir+":"+_env["PATH"]

    try:
        runner = Popen([shell]+shlex.split(args), env=_env, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    except Exception:
        # we could not find that
        return 127

    try:
        # If possible propagnate the sigterm (for #184)
        def handle_term(s, f):
            runner.send_signal(signal.SIGTERM)
        signal.signal(signal.SIGTERM, handle_term)
    except:
        pass

    def do_the_run():
        try:
            runner.wait()
        except KeyboardInterrupt:
            runner.send_signal(signal.SIGINT)
            do_the_run()

    std("Opening a shell ready to compile for you. ")
    do_the_run()

    return runner.returncode

def get_template(name):
    """
    Gets a template file with the given name
    """
    
    # TODO: Find out why this is unused and if we still need it. 
    return read_file(install_dir + "/bin/templates/" + name)
