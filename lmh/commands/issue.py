import webbrowser
from lmh.lib.config import get_config

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Open a url to display issues in the browser"
    def do(self, args, unknown):
        return webbrowser.open(get_config("gl::issue_url"))
