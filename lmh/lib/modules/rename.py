import os
import re
import os.path

from lmh.lib.io import std, err, find_files, read_file, write_file

def rename(where, renamings, simulate = False):
    """Moves modules from source to dest. """

    where = os.path.abspath(where)

    if not os.path.isdir(where):
        err("Cannot rename:", where, "is not a directory. ")
        return False

    if len(renamings) % 2 != 0:
        err("You must provide renamings in pairs. ")
        return False

    if len(renamings) == 0:
        std("Nothing to rename ...")
        return True

    regexes = []
    replaces = []

    # Compile regexes
    i = 0
    while i< len(renamings):

        # What we need to find
        find = renamings[i]
        find_parts = find.split("-")
        find_args = r"\{"+(r"\}\{".join(find_parts))+r"\}"
        find_i = "i"*len(find_parts)

        # What we need to replace
        replace = renamings[i+1]
        replace_parts = replace.split("-")
        replace_args = "{"+("}{".join(replace_parts))+"}"
        replace_i = "i"*len(replace_parts)

        # defi
        regexes.append(re.compile(r"\\def"+find_i+r"\["+find+r"\]"+find_args))
        replaces.append("\\def"+replace_i+"["+replace+"]"+replace_args)

        # defi (Michael)
        regexes.append(re.compile(r"(\\def(?:i{1,3}))\["+find+r"\](\{(?:[^\}]*)\})"))
        replaces.append("\\1["+replace+"]\\2")

        # trefi
        regexes.append(re.compile(r"\\tref"+find_i+r"\[([^\]]*)\]"+find_args))
        replaces.append("\\\\tref"+replace_i+"[\\1]"+replace_args)

        # atrefi
        regexes.append(re.compile(r"\\atref"+find_i+r"\[([^\]]*)\]\{([^\}]*)\}"+find_args))
        replaces.append("\\\\atref"+replace_i+"[\\1]{\\2}"+replace_args)

        # mtrefi
        regexes.append(re.compile(r"\\mtref"+find_i+r"\[([^\]\?]*)\?"+find+r"\]"+find_args))
        replaces.append("\\mtref"+replace_i+"[\\1?"+replace+"]"+replace_args)

        # go to the next pattern.
        i = i+2

    actions = zip(regexes, replaces)

    # Find all the files
    for file in find_files(where, "tex")[0]:
        # Read a file
        content = read_file(file)

        # Run all of the actions
        for (f, r) in actions:
            content = f.sub(r, content)

        write_file(file, content)

    return True
