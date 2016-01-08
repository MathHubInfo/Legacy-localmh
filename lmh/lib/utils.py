"""
Miscellaneous Utility functions
"""
import functools
import os, errno


def remove_doubles(lst):
    """
    Returns a list that contains each of the elements in lst exactly once. 
    """
    
    return list(set(lst))

def reduce(lst):
    """
    Flattens a list by joining nested lists of any level. 
    """
    return sum(([x] if not isinstance(x, list) else reduce(x) for x in lst), [])

def mkdir_p(path):
    """
    Creates a directory and any of its parents if it does not yet exist. 
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def cached(f):
    """
    Decoration to cache functions. 
    """
    return functools.lru_cache()(f)