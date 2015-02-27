import fnmatch

from string import Template

from lmh.lib.io import std, err
from lmh.lib.env import data_dir
from lmh.lib.git import clone, exists
from lmh.lib.repos.local.dirs import is_repo_dir
from lmh.lib.repos.local.package import get_package_dependencies
from lmh.lib.config import get_config

try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen

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



def find_source(name, quiet = False):
    """Finds the source of a repository. """

    root_urls = get_config("install::sources").rsplit(";")
    root_suffix = ["", ".git"]
    for url in root_urls:
        for url_suf in root_suffix:
            if exists(url+name+url_suf):
                return url+name+url_suf
    if not quiet:
        err("Can not find remote repository", name)
        err("Please check install::sources and check your network connection. ")
    return False

def is_valid(name, no_manifest = False):
    """Checks if a remote repository is a valid repository. """

    # If we have install::nomanifest, then
    if no_manifest or get_config("install::nomanifest"):
        return True

    raw = Template(get_config("gl::raw_url")).substitute(repo=name)+"META-INF/MANIFEST.MF"

    try:
        urlopen(raw)
        return True
    except Exception:
        return False



#
# Installing a repository
#

def force_install(rep):
    """Forces installation of a repository"""
    std("Installing", rep)

    # Find the source for the repository
    repoURL = find_source(rep)

    if repoURL == False:
        return False

    # Clone the repo
    return clone(data_dir, repoURL, rep)


def install(no_manifest, *reps):
    """Install a repositories and its dependencies"""

    reps = [r for r in reps]

    if no_manifest == False:
        no_manifest = get_config("install::nomanifest")

    for rep in reps:
        if not is_repo_dir(rep):
            if not force_install(rep):
                err("Unable to install", rep)
                return False

        try:
            if not no_manifest:
                std("Resolving dependencies for", rep)
                for dep in get_package_dependencies(rep):
                    if not (dep in reps) and not is_installed(dep):
                        std("Found unsatisfied dependency:", dep)
                        reps.append(dep)
        except:
            if no_manifest:
                err("Error parsing dependencies for", rep)
                err("Set install::nomanifest to True to disable this. ")
                return False

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


    return filter(lambda x: is_valid(x, no_manifest), sorted(matched_projects))
