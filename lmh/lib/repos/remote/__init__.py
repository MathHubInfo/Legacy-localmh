import fnmatch

from string import Template

from lmh.lib.io import std, err
from lmh.lib.env import data_dir
from lmh.lib.git import clone
from lmh.lib.repos.local.package import get_package_dependencies, is_installed
from lmh.lib.config import get_config

from lmh.lib.repos.indexer import find_source

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

def is_valid(name):
    """Checks if a remote repository is a valid repository. """

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


def install(*reps):
    """Install a repositories and its dependencies"""

    reps = [r for r in reps]

    for rep in reps:
        if not is_installed(rep):
            if not force_install(rep):
                err("Unable to install", rep)
                return False
        else:
            std("Already installed:", "'"+rep+"'")

        try:
            std("Resolving dependencies for", rep)
            for dep in get_package_dependencies(rep):
                if not (dep in reps) and not is_installed(dep):
                    std("Found unsatisfied dependency:", "'"+dep+"'")
                    reps.append(dep)
                else:
                    std("Found statisfied dependency:", "'"+dep+"'")
        except:
            pass
            return False

def ls_remote(*spec):
    """Lists remote repositories matching some specification. """

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


    return filter(lambda x: is_valid(x), sorted(matched_projects))
