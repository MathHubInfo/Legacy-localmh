from lmh.lib.io import err
from lmh.lib.git import exists
from lmh.lib.config import get_config

def find_source(name, quiet = False):
    """
        Finds the source of a repository.
        @param name - Name of repository to find.
        @param quiet - Should we print output.
    """

    # Check if the result is cached.
    # In that case we won't have to query again.
    if name in find_source.cache:
        return find_source.cache[name]


    # Iterate over the root urls
    # and the suffixes.
    root_urls = get_config("install::sources").rsplit(";")
    root_suffix = ["", ".git"]


    for url in root_urls:
        for url_suf in root_suffix:
            # Check if the remote repository exists.
            if exists(url+name+url_suf, False):
                find_source.cache[name] = url+name+url_suf
                return url+name+url_suf

    # We could not find any matching remote.
    # So send an error message unless we are quiet.
    if not quiet:
        err("Can not find remote repository", name)
        err("Please check install::sources and check your network connection. ")

    # and we failed.
    return False

find_source.cache = {}
