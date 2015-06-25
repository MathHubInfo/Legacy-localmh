import webbrowser
from lmh.lib.io import std
from lmh.lib.config import get_config

def do(args, unknown):

    url = get_config("mh::issue_url")
    repo = match_repo(args.repo)

    # if we can not match the repository, exit
    if not repo:
        err("Unable to match repository '"+repo+"'")
        return False

    # Try and open the url
    # and if that fails, just print it.      
    url = url.replace("$name", repo)
    if not webbrowser.open(url):
        std(url)

    return True
