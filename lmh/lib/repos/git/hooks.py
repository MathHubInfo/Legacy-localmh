
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
