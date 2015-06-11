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
def remove_doubles(seq):
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
            std(exc)
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
