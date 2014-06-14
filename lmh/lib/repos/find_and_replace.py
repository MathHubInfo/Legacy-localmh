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

import os
import os.path

import functools

from lmh.lib.io import std, err
from string import Template

def replace(replacer, replace_args, fullPath, m):
    # replace
    std("Replacing in", fullPath)

    # nothing to replace => return the first group
    if replacer == None:
        return m.group(0)

    # generate all the files
    for idx, g in enumerate(m.groups()):
        replace_args["g"+str(idx)] = g

    # do the subitution
    res = Template(replacer).substitute(replace_args)

    return res

def replacePath(dirname, matcher, replaceFnc, apply=False):
    # compile the matcher

    try:
        compMatch = re.compile(matcher)
    except Exception as e:
        err("failed to compile matcher %r"%matcher)
        err(e)
        return False

    for root, dirs, files in os.walk(dirname):
        path = root.split('/')
        for file in files:
            fileName, fileExtension = os.path.splitext(file)
            if fileExtension != ".tex":
                continue
            fullpath = os.path.join(root, file)
            if not os.access(fullpath, os.R_OK): # ignoring files I cannot read
                continue
            changes = False
            replaceContext = functools.partial(replaceFnc, fullpath)
            for line in open(fullpath, "r"):
                newLine = compMatch.sub(replaceContext, line)
                if newLine != line:
                    changes = True
                    std(fullpath + ": \n " + line + newLine)

                if apply:
                    write_file(fullpath+".tmp", newLine)
            if apply:
                if changes:
                    os.rename(fullpath+".tmp", fullpath)
            else:
                os.remove(fullpath+".tmp")

def find(rep, args):
    """Finds pattern in repositories"""

    # Find the given repository
    replacer = None
    repname = match_repo(rep)

    # create a Template that subsitutes $repo with the repository name
    matcher = Template(args.matcher).substitute(repo=repname)

    if args.replace:
        replacer = args.replace[0]
    # some more arguments for the replacer
    replace_args = {"repo" : repname}

    # calll the replacer function
    replaceFnc = functools.partial(replace, replacer, replace_args)

    return replacePath(rep, matcher, replaceFnc, args.apply)
