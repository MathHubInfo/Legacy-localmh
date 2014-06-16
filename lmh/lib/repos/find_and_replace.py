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
import re
from string import Template

from lmh.lib.io import find_files, std, err, read_file, write_file
from lmh.lib.env import data_dir
from lmh.lib.repos.local import find_repo_dir, match_repo

def find_and_replace_file(file, match, replace):
    """Finds and replaces a single file. """

    # Compile thex regexp
    try:
        match_regex = re.compile(match)
    except:
        err("Invalid regular Expression. ")
        return False

    # get the repository
    repo = os.path.relpath(find_repo_dir(file), data_dir)

    # Read file and search
    file_content = read_file(file)
    # We did nothing yet
    did = False

    def replace_match(match):
        # we did something
        did = True

        # Make a template.
        replacer_template = {}
        replacer_template["repo"] = repo
        for i, g in enumerate(match.groups()):
            replacer_template["g"+str(i)] = g

        # And replace in it
        return Template(replace).substitute(replacer_template)

    new_file_content = re.sub(match_regex, replace_match, file_content)

    if file_content != new_file_content:
        std(file)
        # If something has changed, write back the file.
        write_file(file, new_file_content)
    if did:
        std(file)
    return did

def find_file(file, match):
    """Finds inside a single file. """

    # Compile thex regexp
    try:
        match_regex = re.compile(match)
    except:
        err("Invalid regular Expression. ")
        return False

    # Read file and search
    file_content = read_file(file)
    if re.search(match_regex, file_content) != None:
        std(file)
        return True
    else:
        return False


def find_cached(files, match, replace = None):
    """Finds and replaces inside of files. """
    rep = False
    for file in files:
        repo = os.path.relpath(find_repo_dir(file), data_dir)
        matcher = Template(match).substitute(repo=repo)
        if replace != None:
            rep = find_and_replace_file(file, matcher, replace) or rep
        else:
            rep = find_file(file, matcher) or rep
    return rep

def find(rep, args):
    """Finds pattern in repositories"""

    match = args.matcher
    replace = args.replace[0] if args.apply else None

    # Find files in the repository
    files = find_files(match_repo(rep, abs=True), "tex")[0]

    return find_cached(files, match, replace)
