from lmh.lib.io import err
from lmh.lib.git import exists
from lmh.lib.config import get_config

import fnmatch
from string import Template


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
