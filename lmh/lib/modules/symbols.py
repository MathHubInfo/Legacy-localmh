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

import re
import sys
import shutil
from lmh.lib import f7
from lmh.lib.io import std, err, write_file, read_file
from lmh.lib.modules import locate_modules, needsPreamble

def pat_to_match(pat , o = 0):
    # turn it into a match

    if pat[3+o] != "":
        split = pat[3+o].split("-")
        if pat[0] == "adef":
            split = split[1:]
        return [pat[0], len(split), split]

    if pat[0] == "adef":
        o += 2

    if pat[1] == "i":
        return [pat[0], 1, [pat[5+o]]]
    elif pat[1] == "ii":
        return [pat[0], 2, [pat[5+o], pat[7+o]]]
    elif pat[1] == "iii":
        return [pat[0], 3, [pat[5+o], pat[7+o], pat[9+o]]]



def find_all_defis(text):
    # find all a?defs and turn them into nice matches
    pattern = r"\\(def|adef)(i{1,3})(\[(.*?)\])?({([^{}]+)?})({([^{}]+)?})?({([^{}]+)?})?({([^{}]+)?})?"
    vals = [pat_to_match(x) for x in re.findall(pattern, text)]
    return vals

def find_all_symis(text):
    # find all the symis
    pattern = r"\\begin{modsig}((.|\n)*)\\end{modsig}"
    pattern2 = r"\\(sym)(i{1,3})(\*)?(\[(.*?)\])?({([^{}]+)?})({([^{}]+)?})?({([^{}]+)?})?"
    matches = re.findall(pattern, text)
    if len(matches) == 0:
        return []
    text = matches[0][0]
    return [pat_to_match(x, o=1) for x in re.findall(pattern2, text)]

def find_all_symdefs(text):
    # FInd all symdefs
    pattern = r"\\begin{modsig}((.|\n)*)\\end{modsig}"
    pattern2 = r"\\symdef(\[([^\]]*,(\s)*)?name=([^],]+)?(,[^\]]*)?\])?\{([^{}]+)?\}"
    matches = re.findall(pattern, text)
    if len(matches) == 0:
        return []
    text = matches[0][0]
    matches = re.findall(pattern2, text)
    return [m[3] if m[3] != "" else m[5] for m in matches]



def add_symis(text, symis):
    addtext = []
    for sym in symis:
        if sym[1] == 0:
            continue
        addtext.append("\\sym"+("i"*sym[1]) +"{"+"}{".join(sym[2])+"}\n")
    addtext = f7(addtext)
    pattern = r"\\begin{modsig}((.|\n)*)\\end{modsig}"
    return re.sub(pattern, r"\\begin{modsig}\1"+"".join(addtext)+"\\end{modsig}", text)

def warn_symbols(fname, syms, symdefs):
    # fwanr about double things
    for sym in ["-".join(s[2]) for s in syms]:
        if sym in symdefs:
            err(fname+",", "Symbol", sym+": Found both symdef and symi. ")
    return True

def find_sds(fname):
        # skip non-language bindings
        languageFilePattern = r"\.(\w+)\.tex$"

        # Find the associated module
        fmodname = re.sub(languageFilePattern, ".tex", fname)
        content = read_file(fname)

        if len(re.findall(languageFilePattern, fname)) == 0:
            # This is what we have
            syms = find_all_symis(content)
            symdefs = find_all_symdefs(content)

            # for non-language-bndings
            return [warn_symbols(fname, syms, symdefs)]

        # Try and read the other file
        try:
            modcontent = read_file(fmodname)
        except IOError:
            err("Missing module:", fmodname)
            return [False]

        # FInd all the symbolds and definitions
        defs = find_all_defis(content)

        # This is what we have
        syms = find_all_symis(modcontent)
        symdefs = find_all_symdefs(modcontent)

        # Warn about symbols
        warn_symbols(fmodname, syms, symdefs)

        if defs == None:
            defs = []
        if syms == None:
            syms = []

        return (fmodname, defs, syms, symdefs, modcontent)


def add_symbols(fname):
    # Add missing symbols form language bindings to module

    q = find_sds(fname)
    if len(q) == 1:
        # we have already done something
        return q[0]

    (fmodname, defs, syms, symdefs, modcontent) = q

    # check if we still need them
    def need_sym(d):
        # negated
        req = ["sym", d[1], d[2]]
        try:
            name = "-".join(d[2])
        except:
            name = ""

        return not (req in syms) and not (name in symdefs)

    # OK filter them out
    required = filter(need_sym, defs)

    # Add them if we need to
    if len(required) >= 0:
        std("Adding", len(required), "symbol definition(s) from", fname)
        towrite = add_symis(modcontent, required)
        write_file(fmodname, towrite)

    return True

def check_symcomplete(fname):
    # Add missing symbols form language bindings to module

    q = find_sds(fname)
    if len(q) == 1:
        # we have already done something
        return q[0]

    (fmodname, defs, syms, symdefs, modcontent) = q

    # we dont care about the 'i's, we just want the names
    defs = ["-".join(d[2]) for d in defs]
    syms = ["-".join(s[2]) for s in syms]

    # For all the syms and symdefs, check if they are defined in the binding.
    missing = filter(lambda s:not s in defs, syms+symdefs)

    if(len(missing) > 0):
        err(fname, "incomplete: ")
    for m in missing:
        err("Symbol", m, "found in module signature, but missing in language binding. ")


    return True

def check_defs(d):
    # Find all the modules that we have to worry about
    mods = filter(lambda x:x["type"] == "file", locate_modules(d))
    mods = filter(lambda x:needsPreamble(x["file"]), mods)

    ret = True

    for mod in mods:
        ret = ret and check_symcomplete(mod["file"])

    return ret

def check_symbols(d):
    # Find all the modules that we have to worry about
    mods = filter(lambda x:x["type"] == "file", locate_modules(d))
    mods = filter(lambda x:needsPreamble(x["file"]), mods)

    ret = True

    for mod in mods:
        ret = ret and add_symbols(mod["file"])

    return ret
