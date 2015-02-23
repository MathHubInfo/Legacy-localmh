import os.path

from lmh.lib.io import read_file
from lmh.lib.env import install_dir
from lmh.lib.git import do_data


"""lmh lib version"""
version = read_file(install_dir + "/" + "/lmh/data/version")

def git_version():
    """Checks the current gi version of the core"""
    try:
        return do_data(install_dir, "rev-parse", "HEAD")[0].rstrip()
    except:
        return "<Not under source control>"

"""lmh license text"""
license = \
"""
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
