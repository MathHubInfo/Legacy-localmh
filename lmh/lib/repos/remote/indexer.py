import fnmatch
from string import Template

from lmh.lib.io import std, err
from lmh.lib.git import exists
from lmh.lib.config import get_config
from lmh.lib.git import get_remote_status

from string import Template

from lmh.lib.repos.local.package import get_package_dependencies, is_installed, is_upgradable, build_local_tree

try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen

# Import urlopen
# Compatibility Python2 + Python3
try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen

# Import BeautifulSoup
# may fail, but then we skip out on ls-remote.
try:
    from bs4 import BeautifulSoup
except:
    try:
        from BeautifulSoup4 import BeautifulSoup
    except:
        err("Missing beautifulsoup4, please install it. ")
        err("You may want to: ")
        err("   pip install beautifulsoup4")
        err("or")
        err("   pip install lmh --upgrade")
        err("Some things may not be available and fail miserably. ")
        err("See http://www.crummy.com/software/BeautifulSoup/")


        BeautifulSoup = False

def ls_remote(no_manifest, *spec):
    """Lists remote repositories matching some specification. """

    if no_manifest == False:
        no_manifest = get_config("install::nomanifest")

    if BeautifulSoup == False:
        err("BeautifulSoup not found. ")
        return False

    if len(spec) == 0:
        spec = ["*"]

    # The basic url
    base_url = get_config("gl::projects_url")
    projects = set()
    def filter_page_name(p):
        while(p.startswith("/")):
            p = p[1:]
        return p

    for i in range(1, 100):
        # the project pages url
        url = base_url+'?page='+str(i)

        # make the request
        try:
            response = urlopen(url)
            soup = BeautifulSoup(response.read())
        except:
            err("Unable to make connection")
            break

        try:
            # find the project pages
            soup = soup.find("div", {"class": "public-projects"})
            soup = soup.find("ul")

            # Nothing here, break
            if soup.find("div", {"class": "nothing-here-block"}):
                break

            for h4 in soup.findAll("h4"):
                projects.add(filter_page_name(h4.find("a")["href"]))
        except Exception as e:
            err(e)
            err("Parsing failure (make sure gl::projects_url is correct)")

    matched_projects = set()

    for s in spec:
        matches = [p for p in projects if fnmatch.fnmatch(p, s)]
        if len(matches) == 0:
            matches = [p for p in projects if fnmatch.fnmatch(p, s+"/*")]
        if len(matches) == 0:
            if find_source(s, True):
                matches = [s]
            else:
                err("Warning: No modules matching", s, "found. ")
        matched_projects.update(matches)

    # TODO: Check if we need to filter these somehow (check for access?)
    return sorted(matched_projects)

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
    meta_inf_url = Template(get_config("gl::raw_url")).substitute(repo=repo)+"META-INF/MANIFEST.MF"

    # Tell the user we are trying to read META-INF information.
    std("Reading remote META-INF information for", repo)

    try:
        # Fetch the url
        meta_inf_content = urlopen(meta_inf_url)

        # Read the content
        fetch_metainf.cache[repo] = str(meta_inf_content.read())

        # and return it.
        return fetch_metainf.cache[repo]
    except Exception as e:
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
    return get_package_dependencies(repo, meta_inf)

def build_remote_tree(repos, no_locals = False):
    """
        Builds a remote dependency tree.

        @param repo {string} - Repository to check.
    """
    # We want to iterate through these repos.
    repos = set(repos)

    # Packages that can be installed.
    installable = set([])

    # Packages that are missing.
    missing = set([])

    while len(repos) != 0:
        # Iterate through the repositories.
        r = repos.pop()

        # If we do not want locals and are already installed, skip
        if no_locals and is_installed(r):
            continue

        # If we already did something, continue.
        if r in installable or r in missing:
            continue

        # If we know the source, we can add the deps to scan.
        if find_source(r):
            try:
                repos.update(get_repo_deps(r))
                installable.add(r)
            except:
                missing.add(r)
        else:
            missing.add(r)

    return (list(installable), list(missing))
def build_deps_tree_noupgrade(*repo):
    """
        Builds the dependency tree for the installation of a repository.
        Does not consider

        @param* repo {string[]} - Repositories to install.
    """

    # All of the repositories.
    repos = list(repo)

    #
    # TREE to be built.
    #

    # TODO: Have variables here.

    #
    # Make the tree
    #
    (installed, missing) = build_local_tree(*repo)

    # Stuff to be installed
    installed = set(installed)

    # Find all the remote depencies and ignore local ones.
    (remote_exists, missing) = build_remote_tree(missing, no_locals = True)

    print(installed, remote_exists, missing)
