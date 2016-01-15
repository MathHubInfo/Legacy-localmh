from lmh.lib.io import err
from lmh.lib.git import exists
from lmh.lib.config import get_config

import fnmatch
from string import Template

from urllib.request import urlopen

try:
    import lxml.html
except ImportError:
    lxml = False

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

    if lxml == False:
        err("Missing lxml module")
        err("If you are using localmh_docker you might want to:")
        err("  lmh docker pull")
        err("and re-create the image or manually run:")
        err("   lmh docker sshell; pip3 install lxml ; exit")
        err("to install it")
        
        return False

    if len(spec) == 0:
        spec = ["*"]

    # The basic url
    base_url = "http://gl.mathhub.info/public/"
    projects_per_page = 20
    projects = set()

    for i in range(1, 100):
        # the project pages url
        url = base_url+'?page='+str(i)

        # make the request
        try:
            response = urlopen(url)
            response = response.read()
            
        except:
            err("Unable to make connection")
            break

        try:
            # parse the html
            project_list_page = lxml.html.fromstring(response)
            
            # find all <a class='project'> .hrefs
            new_projects = project_list_page.xpath("//a[@class='project']/@href")
            
            # and remove the starting /s
            new_projects = list(map(lambda s:s[1:] if s.startswith("/") else s, new_projects))
            
            # if we have fewer projects then the max, we can exit now
            if len(new_projects) < projects_per_page:
                break
            
            projects.update(new_projects)
            
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

    return sorted(matched_projects)
