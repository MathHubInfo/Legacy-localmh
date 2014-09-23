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
import os, errno
from time import sleep

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
    """Flattens a list. """
    return sum( ([x] if not isinstance(x, list) else reduce(x) for x in lst), [] )
def f7(seq):
    """Removes doubles from a list efficiently. """
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]
def mkdir_p(path):
    """Make a direcories and its parents"""
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def popen_wait_timeout(process, time):
    """Like process.wait, but with a timeout in milliseconds"""
    polling_interval = 0.1

    while True:
        sleep(polling_interval)
        time = time - polling_interval
        process.poll()
        if process.returncode != None:
            process.wait()
            return True
        elif time < 0:
            # we ran out of time, kill the child
            process.kill()
            return False

def clean_list(lst, key=lambda x:x):
    """Removes doubles from a list using a key"""

    keys = []
    res = []

    for l in lst:
        k = key(l)
        if k in keys:
            pass
        else:
            res.append(l)
            keys.append(k)

    return res
