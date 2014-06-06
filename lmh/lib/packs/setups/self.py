"""
This file is part of LMH.

LMH is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LMH is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LMH.  If not, see <http://www.gnu.org/licenses/>.
"""

from lmh.lib.io import err
from lmh.lib.env import install_dir
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
