import lmh.lib.repos.git.deploy as deploy
from lmh.lib.io import std

def hook_pre_install(rep):
    """
        Hook that runs before installation of a repository.
    """
    return True

def hook_pre_pull(rep):
    """
        Hook that runs before pull of a repository.
    """

    return True

def hook_pre_push(rep):
    """
        Hook that runs before push of a repository.
    """

    return True

def hook_post_update(rep):
    """
        Hook that runs after any change to a repository.
    """

    dbranch = deploy.get_deploy_branch(rep)

    if dbranch:
        std()

        if deploy.installed(rep):
            std("Updating deploy branch '"+dbranch+"' ...")
            deploy.pull(rep, dbranch)
        else:
            std("Installing deploy branch '"+dbranch+"' ...")
            deploy.install(rep, dbranch)
    return True

def hook_post_install(rep):
    """
        Hook that runs before installation of a repository.
    """
    return hook_post_update(rep)

def hook_post_pull(rep):
    """
        Hook that runs after pull of a repository.
    """

    return hook_post_update(rep)

def hook_post_push(rep):
    """
        Hook that runs after push of a repository.
    """

    return hook_post_update(rep)
