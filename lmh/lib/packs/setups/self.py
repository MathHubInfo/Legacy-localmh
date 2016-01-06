from lmh.lib.io import std
from lmh.lib.dirs import install_dir
from lmh.lib.git import pull

from lmh.lib.packs.classes import Pack, UnsupportedAction

class SelfPack(Pack):
    """A Package representing lmh itself. """
    def do_update(self, pack_dir, update):
        return pull(install_dir)
    def do_remove(self, pack_dir, params):
        raise UnsupportedAction
    def is_installed(self, pack_dir):
        return True

setup = SelfPack("self")
