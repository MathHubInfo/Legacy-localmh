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

from lmh.lib.packs.classes import Pack, UnsupportedAction

class AutcompletePack(Pack):
    """A Package representing lmh autocompletion. """
    def do_install(self, pack_dir, params):
        err("Autocomplete Installation is currently disabled. ")
        err("Please try installing the python package")
        err("argparse")
        err("Manually. ")
    def do_update(self, pack_dir, params):
        raise UnsupportedAction
    def do_remove(self, pack_dir, params):
        raise UnsupportedAction
    def is_installed(self, pack_dir):
        try:
            import argparse
            return True
        except:
            return False

setup = AutcompletePack("autocomplete")
