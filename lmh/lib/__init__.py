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

# Set the version information
from lmh.lib.about import version as __version__


# Misc util functions

def shellquote(s):
	"""shellquotes arguments"""
	return "'" + s.replace("'", "'\\''") + "'"

def setnice(nice, pid = None):
    """ Set the priority of the process to below-normal."""

    import psutil, os
    if pid == None:
      pid = os.getpid()

    p = psutil.Process(pid)
    p.nice = nice

def reduce(lst):
  return sum( ([x] if not isinstance(x, list) else reduce(x)
         for x in lst), [] )