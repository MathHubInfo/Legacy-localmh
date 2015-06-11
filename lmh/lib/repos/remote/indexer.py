
from lmh.lib.io import err
from lmh.lib.git import exists
from lmh.lib.config import get_config

from lmh.lib.repos.local.package import get_package_dependencies, is_installed, build_local_tree

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
            if exists(url+name+url_suf):
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

def is_upgardable(repo):
    """
        Checks if a repo is upgradable.
    """
    # TODO: implement this.

    return False

def fetch_metainf(repo):
    """
        Fetches the remote META-INF file.

        @param repo Repository to fetch meta inf from.
    """

    # Check if it is already cached.
    # It probably isn't but why not?
    if repo in fetch_metainf.cache:
        return fetch_metainf.cache[repo]

    # build the url
    meta_inf_url = Template(get_config("gl::raw_url")).substitute(repo=name)+"META-INF/MANIFEST.MF"

    try:
        # Fetch the url
        meta_inf_content = urlopen(raw)

        # Read the content
        fetch_metainf.cache[repo] = str(meta_inf_content.read())

        # and return it.
        return fetch_metainf.cache[repo]
    except:
        return False

fetch_metainf.cache = {}

def get_repo_deps(repo):
    """
        Fetches the (remote) dependencies of a repository.

        @param repo {string} Repository to find dependecies from

        @returns {string[]}
    """

    # Fetch the META INF file
    meta_inf = fetch_metainf(repo)

    # If we don't have a meta inf, return
    if not meta_inf:
        return []

    # Split it into lines.
    meta_inf = meta_inf.split("\n")

    # Parse the dependencies.
    deps = get_package_dependencies(repo, meta_inf)

def build_deps_tree(*repo):
    """
        Builds the dependency tree for the installation of a repository.

    """

    # Build the repos to be installed.
    repos = repos[:]

    # The repositories to be installed anew.
    install = set()

    # Repositories already installed.
    installed = set()

    # Repositories to be upgraded.
    upgradable = set()

    # Iterate through all the repositories.
    while len(repos) != 0:

        # Take the first repository
        r = repos.pop()

        # If we have already treated them, go to the next iteration.
        if r in install or r in installed:
            continue

        # If it is already installed
        # Build the local deps tree
        if is_installed(r):

            # It is already installed.
            installed.add(r)

            # Build the local tree
            (already_here, missing) = build_local_tree(r)

            # Add the ones that are already
            # and those that are missing
            # to the repositories to be scanned.
            repos.extend(already_here)
            repos.extend(missing)
        else:
            # Add the new one to be installed. 
            install.add(r)

    # TODO: Check for upgradable
    # and their **new** dependencies.
