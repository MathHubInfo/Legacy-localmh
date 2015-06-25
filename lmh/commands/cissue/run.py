import webbrowser
from lmh.lib.io import std
from lmh.lib.config import get_config

def do(args, unknown):

    if not webbrowser.open(get_config("mh::issue_url")):
        std(get_config("mh::issue_url"))

    return True
