from lmh.lib.io import std
from lmh.lib.dirs import lmh_locate
from lmh.lib.git import pull

from lmh.lib.packs.classes import Pack, UnsupportedAction

class SelfPack(Pack):
    """A Package representing lmh itself. """
    def do_update(self, pack_dir, update):
        return pull(lmh_locate)
    def do_remove(self, pack_dir, params):
        raise UnsupportedAction
    def is_installed(self, pack_dir):
        return True

setup = SelfPack("self")
