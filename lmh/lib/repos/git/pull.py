from lmh.lib.io import term_colors, std
from lmh.lib.repos.git.install import install
from lmh.lib.git import push as git_push
from lmh.lib.git import pull as git_pull
from lmh.lib.git import get_remote_status
from lmh.lib.repos.local.dirs import match_repo


def pull(verbose, *repos):
    """Pulls all currently installed repositories and updates dependencies"""

    # Check if we need to update the local repository
    def needs_updating(rep):
        state = get_remote_status(rep)
        return state == "pull" or state == "failed" or state == "divergence"

    ret = True

    for rep in repos:
        std("git pull", rep, newline=False)

        if verbose or needs_updating(rep):
            std()
            rgp = git_pull(rep)
            ret = rgp and ret
            rep = match_repo(rep)
            if rgp:
                std("Updated repository", term_colors("green")+rep+term_colors("normal"))
                ret = install(rep) and ret
            else:
                std("Did not update", term_colors("red")+rep+term_colors("normal"), "(merge conflicts or network issues)")
        else:
            rep = match_repo(rep)
            std("")
            std("Nothing to pull for", term_colors("green")+rep+term_colors("normal"))

    return ret
