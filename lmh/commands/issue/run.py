import webbrowser
from lmh.lib.io import std
from lmh.lib.config import get_config

def do(args, unknown):

    if not webbrowser.open(get_config("gl::issue_url")):
        std(get_config("gl::issue_url"))

    return True
