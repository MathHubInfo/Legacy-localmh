from lmh.lib.io import std
from lmh.lib.env import install_dir

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Show the root directory of the lmh installation"
    def do(self, args, unknown):
        std(install_dir)
        return True
