import re
from lmh.lib.utils import remove_doubles
from lmh.lib.io import std, err, write_file, read_file
from lmh.lib.modules import locate_files, needsPreamble

def def_pat_to_match(pat , o = 0):
    # turn it into a match

    if pat[3+o] != "":
        split = pat[3+o].split("-")
        if pat[0] == "adef":
            split = split[1:]
        return [pat[0], len(split), split]

    if pat[0] == "adef":
        o += 2

    if pat[1] == "i":
        res = [pat[0], 1, [pat[5+o]]]
    elif pat[1] == "ii":
        res = [pat[0], 2, [pat[5+o], pat[7+o]]]
    elif pat[1] == "iii":
        res = [pat[0], 3, [pat[5+o], pat[7+o], pat[9+o]]]

    # Normalise for issue #166
    res[2] = "-".join(res[2]).split("-")
    res[1] = len(res[2])
    
    return res

def ass_pat_tp_match(pat):
    terms = "-".join(res[2]).split("-")
    return ['def', len(terms), terms]


def find_all_defis(text):

    # pattern for the a?defi*s
    def_pattern = r"\\(def|adef)(i{1,3})(\[(.*?)\])?({([^{}]+)?})({([^{}]+)?})?({([^{}]+)?})?({([^{}]+)?})?"
    def_vals = [def_pat_to_match(x) for x in re.findall(def_pattern, text)]

    # pattern for assdef
    ass_pattern = r"\\assdef({([^{}]+)?})({([^{}]+)?})"
    ass_vals = [ass_pat_tp_match(x) for x in re.findall(ass_pattern, text)]

    return def_vals + ass_vals

def find_all_symis(text):
    # find all the symis
    pattern = r"\\begin{modsig}((.|\n)*)\\end{modsig}"
    pattern2 = r"\\(sym)(i{1,3})(\*)?(\[(.*?)\])?({([^{}]+)?})({([^{}]+)?})?({([^{}]+)?})?"
    matches = re.findall(pattern, text)
    if len(matches) == 0:
        return []
    text = matches[0][0]
    return [def_pat_to_match(x, o=1) for x in re.findall(pattern2, text)]

def find_all_symdefs(text):
    # FInd all symdefs
    pattern = r"\\begin{modsig}((.|\n)*)\\end{modsig}"
    pattern2 = r"\\symdef(\[([^\]]*,(\s)*)?name=([^],]+)?(,[^\]]*)?\])?\{([^{}]+)?\}"
    pattern3 = r"\\symdef(\[([^\]]+)\])?\{([^{}]+)?\}"
    matches = re.findall(pattern, text)
    if len(matches) == 0:
        return []
    text = matches[0][0]

    # Find symdefs with seperate names
    matches = re.findall(pattern2, text)
    names_1 = [m[3] if m[3] != "" else m[5] for m in matches]

    # and without seperate names
    matches2 = re.findall(pattern3, re.sub(pattern2, "", text))
    names_2 = [m[2] for m in matches2]

    # and combine
    return remove_doubles(names_1+names_2)



def add_symis(text, symis):
    addtext = []
    for sym in symis:
        if sym[1] == 0:
            continue
        addtext.append("\\sym"+("i"*sym[1]) +"{"+"}{".join(sym[2])+"}\n")
    addtext = remove_doubles(addtext)
    pattern = r"\\begin{modsig}((.|\n)*)\\end{modsig}"
    return re.sub(pattern, r"\\begin{modsig}\1"+"".join(addtext)+"\\end{modsig}", text)

def warn_symbols(fname, syms, symdefs, warns):

    # fwanr about double things
    for sym in ["-".join(s[2]) for s in syms]:
        if sym in symdefs:
            # Only make a warning if wehaven't done so already
            warn = (sym, fname)
            if not (warn in warns):
                warns.append(warn)
                err(fname+",", "Symbol", sym+": Found both symdef and symi. ")
    return True

def find_sds(fname, warns=[]):
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
        return [warn_symbols(fname, syms, symdefs, warns)]

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
    warn_symbols(fmodname, syms, symdefs, warns)

    if defs == None:
        defs = []
    if syms == None:
        syms = []

    return (fmodname, defs, syms, symdefs, modcontent)


def add_symbols(fname, warns=[]):
    # Add missing symbols form language bindings to module

    q = find_sds(fname, warns)
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

        # Normalise for issue #166
        req[2] = "-".join(req[2]).split("-")
        req[1] = len(req[2])

        # We have an empty argument, what's this?
        if name == "":
            # it is empty
            return False

        return not ((req in syms) or (name in symdefs))

    # OK filter them out
    required = list(filter(need_sym, defs))

    # Add them if we need to
    if len(required) > 0:
        std("Adding", len(required), "symbol definition(s) from", fname)
        towrite = add_symis(modcontent, required)
        write_file(fmodname, towrite)

    return True

def check_symcomplete(fname, warns=[]):
    # Add missing symbols form language bindings to module

    q = find_sds(fname, warns)
    if len(q) == 1:
        # we have already done something
        return q[0]

    (fmodname, defs, syms, symdefs, modcontent) = q

    # we dont care about the 'i's, we just want the names
    defs = ["-".join(d[2]) for d in defs]
    syms = ["-".join(s[2]) for s in syms]

    # For all the syms and symdefs, check if they are defined in the binding.
    missing = list(filter(lambda s:not s in defs, syms+symdefs))

    if(len(missing) > 0):
        err(fname, "incomplete: ")
    for m in missing:
        err("Symbol", m, "found in module signature, but missing in language binding. ")


    return True

def check_defs(d):
    # Cache for all the warnings
    warns = []

    # Find all the modules that we have to worry about
    mods = locate_files(d)
    mods = list(filter(lambda x:needsPreamble(x), mods))

    ret = True

    for mod in remove_doubles(mods):
        ret = ret and check_symcomplete(mod["file"], warns)

    return ret

def check_symbols(d):

    # Cache for all the warnings
    warns = []

    # Find all the modules that we have to worry about
    mods = locate_files(d)
    mods = list(filter(lambda x:needsPreamble(x), mods))

    ret = True

    for mod in remove_doubles(mods):
        ret = ret and add_symbols(mod, warns)

    return ret
