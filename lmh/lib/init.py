import os.path

from lmh.lib.env import which, install_dir
from lmh.lib.io import std, read_raw, find_files
from lmh.lib.about import version
from lmh.lib.git import git_do

# Force reload lmh.lib.config
import lmh.lib.config
try:
    from imp import reload
    reload(lmh.lib.config)
except:
    reload(lmh.lib.config)
from lmh.lib.config import get_config, set_config

def init():
    """Checks if init code has to be run. """
    if get_config("state::lastversion") == version:
        # First run is done
        return True

    # First run
    first_run()
    set_config("state::lastversion", version)

    return True

def post_update():
    # Find the files
    cache = [os.remove(f) for f in find_files(os.path.join(install_dir, "lmh"), "pyc")[0]]
    std("Cleared python cache, removed", len(cache), "files. ")
    # Migrate to github if we haven't already
    if not get_config("self::is_github"):
        git_do(install_dir, "remote", "set-url", "origin", "https://github.com/KWARC/localmh")
        set_config("self::is_github", True)
        std("=== LMH has been moved to Github===")
        std("Please run lmh selfupdate (again) to make sure that you are up-to-date. ")
    return True

def q_program(pgr):
    """Asks the user for the location for an executable. """
    res = read_raw("Where is the "+pgr+" executable? Leave blank to autodetect at runtime. >")
    if res != "":
        res = which(res)
        std("Using", pgr, "at", res)
        set_config("env::"+pgr, res)

def first_run():
    """Inital run code for lmh. """
    std("Welcome to lmh. ")
    std("This seems to be the first time you are running this version of lmh. ")
    std("This setup routine will automatically run and help you configure lmh automatically. ")

    if read_raw("Do you wish to continue? hit enter to continue or enter s to skip. ") != "":
        std("Skipping setup. ")
        return

    # Query for the API key
    res = read_raw("Enter your gitlab private token. Leave blank to prompt for username / password when needed. >")
    if res != "":
        set_config("gl::private_token", res)


    res = ""
    while not res in ["y", "n"]:
        res = read_raw("Do you want to enable output colors[y/n]? >").lower()

    if res == "y":
        std("Colors enabled. ")
        set_config("self::colors", "true")

    res = ""
    while not res in ["y", "n"]:
        res = read_raw("Do you want to use a pager to page long outputs[y/n]? >").lower()

    if res == "y":
        try:
            res = ""
            while which(res) == None:
                res = read_raw("Which pager do you want to use (How about less)? >")

            res = which(res)

            std("Using pager:", res)
            set_config("env::pager", res)

        except KeyboardInterrupt:
            std("Not using any pager. ")

    q_program("git")
    q_program("svn")
    q_program("pdflatex")
    q_program("perl")
    q_program("java")
    q_program("cpanm")
    q_program("make")
    q_program("tar")

    res = ""
    while not res in ["y", "n"]:
        res = read_raw("Do you want to re-run this setup for future versions[y/n]? >").lower()

    if res == "n":
        std("Setup disabled for future versions. ")
        set_config("self::showfirstrun", False)

    #res = ""
    #while not res in ["y", "n"]:
    #       res = read_raw("Do you want lmh to enable some eastereggs[y/n]? >").lower()

    res = "y" # TODO: Set this back to normal.

    if res == "y":
        set_config("::eastereggs", True)

    read_raw("Setup complete. Press enter to continue. ")
    return True
