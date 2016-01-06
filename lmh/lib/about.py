"""
Information about the license and version of lmh
"""

from lmh.lib.utils import cached
from lmh.lib.io import read_file
from lmh.lib.dirs import install_dir
from lmh.lib.git import do_data

@cached
def version():
    """
    Returns the current version of lmh
    """
    return read_file(install_dir + "/" + "/lmh/data/version")

@cached
def git_version():
    """
    Returns the current git version of lmh as a string or None
    """
    try:
        return do_data(install_dir, "rev-parse", "HEAD")[0].rstrip()
    except:
        return None

@cached
def license_text():
    """
    Returns the current license text of lmh
    """
    return """
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""