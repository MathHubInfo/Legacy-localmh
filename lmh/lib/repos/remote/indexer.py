import fnmatch
from string import Template

from lmh.lib.io import err
from lmh.lib.git import exists
from lmh.lib.config import get_config

from lmh.lib.repos.local.package import get_package_dependencies, is_installed, build_local_tree

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

    try:
        # Fetch the url
        meta_inf_content = urlopen(meta_inf_url)

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
    return get_package_dependencies(repo, meta_inf)

def build_deps_tree(*repos):
    """
        Builds the dependency tree for the installation of a repository.
    """

    # TODO: Implement upgradable here somehow.

    # Build the repos to be installed.
    repos = repos[:]

    # The repositories to be installed anew.
    install = set()

    # The repositories we will have to install as a dependency.
    install_deps = set()

    # Depencies already installed.
    installed_deps = set()

    # Repositories already installed.
    installed = set()

    # Iterate through all the repositories.
    while len(repos) != 0:

        # Take the first repository
        r = repos.pop()

        # If we have already treated them, go to the next iteration.
        if r in install or r in installed or r in installed_deps:
            continue

        # If it is already installed
        # Build the local deps tree
        if is_installed(r):

            # It is already installed.
            installed.add(r)

            # Build the local tree
            (already_here, missing) = build_local_tree(r)

            # We add the repositories that are already installed
            installed_deps.extend(already_here)
            
            repos.extend(missing)
        else:
            # Add the new one to be installed.
            install.add(r)

    # Now for the remaining ones (which we need as dependencies)
    # build the complete remote tree and add them everywhere.
    while len(repos) != 0:

        # iterate through the ones we have to install from the remote.
        r = repos.pop()

        # If we already had them, continue.
        if r in install or r in installed or r in installed_deps or r in install_deps:
            continue
        # The dependency we have to add.
        install_deps.add/

    # Now for the missing
