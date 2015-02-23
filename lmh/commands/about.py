from lmh.lib import about
from lmh.lib.io import std

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Show version and general information"

    def do(self, arguments, unparsed):
        std("lmh, Version", about.version, "( git", about.git_version(), ")")
        std()
        std(about.license)

        return True
