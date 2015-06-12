import webbrowser
from lmh.lib.config import get_config

def do(args, unknown):
    return webbrowser.open(get_config("gl::issue_url"))
