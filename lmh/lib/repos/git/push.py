from lmh.lib.io import term_colors, std
from lmh.lib.repos.git.install import install
from lmh.lib.git import push as git_push
from lmh.lib.git import pull as git_pull
from lmh.lib.git import get_remote_status
from lmh.lib.repos.local.dirs import match_repo

def push(verbose, *repos):
    """Pushes all currently installed repositories. """

    # Check if we need to update the local repository
    def needs_updating(rep):
        state = get_remote_status(rep)
        return state == "push" or state == "failed" or state == "divergence"

    ret = True
    
    repos = list(filter(lambda x:x, [r.strip() for r in repos]))

    for rep in repos:
        std("git push", rep, "", newline = False)

        if verbose or needs_updating(rep):
            std()
            ret = git_push(rep) and ret
        else:
            std("OK, nothing to push. ")

    return ret
