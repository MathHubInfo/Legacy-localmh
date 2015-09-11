from lmh.lib.io import std, err, term_colors
from lmh.lib.env import data_dir
from lmh.lib.git import clone
from lmh.lib.repos.local.package import get_package_dependencies, is_installed
from lmh.lib.repos.indexer import find_source

from lmh.lib.repos.git.hooks import hook_pre_install, hook_post_install

def do_deps_install(rep):
    """
        Runs a dependency check.
    """

    std("Looking for dependencies ...")

    deps = []

    try:
        for dep in get_package_dependencies(rep):
            if not is_installed(dep):
                std("   unsatisfied dependency: ", "'"+dep+"'")
            else:
                std("   satisfied dependency:", "'"+dep+"'")
            deps.append(dep)
    except Exception as e:
        std(e)
        err("Failed.")
        return (False, deps)

    std("Done. ")

    return (True, deps)

def do_install(rep):
    """
        Installs a single repository.
    """

    # pre-installation hook.
    std("Running pre-installation hook for '"+rep+"' ... ", newline=False)

    if not hook_pre_install(rep):
        err("Failed. ")
        return (False, [])
    std("Done. ")

    # Find the remote.
    std("Finding remote for '"+rep+"' ... ")
    repoURL = find_source(rep)

    # Did we find a url?
    if repoURL == False:
        std("")
        err("   Could not find a remote. ")
        return (False, [])

    std("   OK, will clone from '"+repoURL+"'")

    # Clone the repository.
    if not clone(data_dir, repoURL, rep):
        err("git clone did not exit cleanly, cloning failed. ")
        err("""
Most likely your network connection is bad. 
If you are using localmh_docker make sure that you have internet access inside the virtual machine. 
""")
        return (False, [])

    std("   OK. ")

    # post-installation hook.
    std("Running post-installation hook for '"+rep+"' ... ", newline=False)

    if not hook_post_install(rep):
        err("Failed. ")
        return (False, [])
    std("Done. ")

    # Check for dependencies.
    return do_deps_install(rep)

def install(*reps):
    """Install a repositories and its dependencies"""
    
    reps = list(filter(lambda x:x, [r.strip() for r in reps]))

    for rep in reps:
        if not is_installed(rep):
            std("Starting installation:         ", term_colors("blue")+"'"+rep+"'"+term_colors("normal"))
            (res, deps) = do_install(rep)

            if not res:
                err("Failed installation:           ", term_colors("red")+"'"+rep+"'"+term_colors("normal"))
                ret = False
            else:
                std("Finished installation:         ", term_colors("green")+"'"+rep+"'"+term_colors("normal"))
                reps.extend([d for d in deps if not d in reps])
        else:
            std("Re-scanning for dependencies: ", term_colors("blue")+"'"+rep+"'"+term_colors("normal"))

            (res, deps) = do_deps_install(rep)

            if not res:
                err("Failed scan:                  ", term_colors("red")+"'"+rep+"'"+term_colors("normal"))
            else:
                std("Finished scan:                ", term_colors("green")+"'"+rep+"'"+term_colors("normal"))
                reps.extend([d for d in deps if not d in reps])
