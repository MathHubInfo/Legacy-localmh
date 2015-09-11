from lmh.lib.io import term_colors, std, err
from lmh.lib.repos.git.install import install
from lmh.lib.git import push as git_push
from lmh.lib.git import pull as git_pull
from lmh.lib.git import get_remote_status
from lmh.lib.repos.local.dirs import match_repo

from lmh.lib.repos.git.hooks import hook_pre_pull, hook_post_pull
from lmh.lib.repos.git.install import install



def do_pull(rep, needs_update):
    """
        Actually pulls a repository.
    """

    # pre-installation hook.
    std("Running pre-update hook for '"+rep+"' ... ", newline=False)

    if not hook_pre_pull(rep):
        err("Failed. ")
        return (False, [])

    std("Done. ")

    ret = True

    if needs_update:
        std("Running git pull ...")
        rgp = git_pull(match_repo(rep, abs=True))
        ret = rgp and ret
        if rgp:
            std("OK")
        else:
            err("Failed (merge conflicts or network issues?)")
            ret = False
    else:
        std("Nothing to pull ...")

    std("Running post-update hook for '"+rep+"' ... ", newline=False)
    if not hook_post_pull(rep):
        err("Failed. ")
        return (False, [])
    std("Done. ")

    return ret

def pull(verbose, *repos):
    """Pulls all currently installed repositories and updates dependencies"""

    # Check if we need to update the local repository
    def needs_updating(rep):
        rep = match_repo(rep, abs=True)
        if verbose:
            return True
        state = get_remote_status(rep)
        return state == "pull" or state == "failed" or state == "divergence"

    ret = True

    repos = list(filter(lambda x:x, [r.strip() for r in repos]))

    for rep in repos:
        std(    "Starting update:           ", term_colors("blue")+"'"+rep+"'"+term_colors("normal"))

        if not do_pull(rep, needs_updating(rep)):
            std("Update failed:             ", term_colors("red")+"'"+rep+"'"+term_colors("normal"))
            ret = False
        else:
            std("Update suceeded:           ", term_colors("green")+"'"+rep+"'"+term_colors("normal"))

    std("Re-installing updated repositories ...")
    return ret and install(*repos)
