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
import shutil

from lmh.lib.modules.symbols import add_symbols

import lmh.lib.io
from lmh.lib.io import read_file, write_file, std, err

def create_multi(modname, *langs):
    if len(langs) == 0:
        err("You need to create at least one language. ")
        return False
    lang = langs[0]

    # Read the module
    try:
        content = read_file(modname+".tex")
    except:
        err("Unable to read original module", modname+".tex")
        return False

    # Module content
    module_content_regex = r"^((?:.|\n)*)\\begin\{module\}\[(?:(.*),\s*)?id=([^,\]]*)(?:\s*(.*))\]((?:.|\n)*?)\\end\{module\}((?:.|\n)*)$"
    module_not_def_regex = r"(?:^|\\end\{definition\})((?:.|\n)*?)(?:\\begin\{definition\}|$)"
    module_def_regex = r"(\\begin\{definition\}(?:(?:.|\n)*?)\\end\{definition\})"

    # Find the module
    mod_content = re.findall(module_content_regex, content)

    if len(mod_content) != 1:
        err("Expected exactly one module environment. (Is the module really monolingual?)")
        return False

    mod_content = mod_content[0]

    # Main Language Content
    main_module = ""
    main_language = ""

    # Prefix and suffix to add to the module
    mod_prefix = mod_content[0]
    mod_suffix = mod_content[5]

    # Id of the module
    mod_id = mod_content[2]
    mod_meta = mod_content[1]+mod_content[3]

    # Definition code
    mod_env_defs = re.findall(module_def_regex, mod_content[4])
    mod_env_nodefs = list(re.findall(module_not_def_regex, mod_content[4]))

    # Assemble the main module
    main_module = mod_prefix
    main_module += "\\begin{modsig}{"+lang+"}"
    main_module += "".join(mod_env_nodefs)
    main_module += "\\end{modsig}"
    main_module += mod_suffix

    try:
        write_file(modname+".tex", main_module)
    except:
        err("Unable to write", modname+".tex")
        return False

    # Assemble the main language binding
    main_language = mod_prefix
    main_language += "\\begin{modnl}["+mod_meta+"]{"+mod_id+"}{"+lang+"}\n"
    main_language += "\n".join(mod_env_defs)
    main_language += "\n\\end{modnl}"
    main_language += mod_suffix

    try:
        write_file(modname+"."+lang+".tex", main_language)
    except:
        err("Unable to write", modname+"."+lang+".tex")
        return False

    lmh.lib.io.__supressStd__ = True

    # Add the symbols frome the language file name
    add_symbols(modname+"."+lang+".tex")

    # Translate to all the other languages
    for l in langs[1:]:
        if not transmod(modname, lang, l):
            lmh.lib.io.__supressStd__ = False
            return False
    lmh.lib.io.__supressStd__ = False

    std("Created multilingual module", modname+".tex")

    # Thats it.
    return True



def transmod(modname, org_lang, dest_lang):
    """Translate a module from one language to another. """

    orfn = modname+"."+org_lang+".tex"
    newfn = modname+"."+dest_lang+".tex"

    try:
        content = read_file(orfn)
    except:
        err("Unable to read original module", orfn)
        return False

    # Replace modnl and viewnl 3rd argument
    content = re.sub(r"(\\begin\{modnl\}\[[^\]]*\]\{[^\}]*\})\{"+org_lang+r"\}", r"\1{"+dest_lang+"}", content)
    content = re.sub(r"(\\begin\{viewnl\}\[[^\]]*\]\{[^\}]*\})\{"+org_lang+r"\}", r"\1{"+dest_lang+"}", content)

    def replacer(match):
        content = match.group(2)

        # trefi -> mtrefi
        content = re.sub(r"\\trefi\[([^\]]*)\]\{([^\}]*)\}", r"\\mtrefi[\1?\2]{\\ttl{\2}}", content)
        # trefii -> mtrefii
        content = re.sub(r"\\trefii\[([^\]]*)\]\{([^\}]*)\}\{([^\}]*)\}", r"\\mtrefii[\1?\2-\3]{\\ttl{\2 \3}}", content)
        # trefiii -> mtrefiii
        content = re.sub(r"\\trefiii\[([^\]]*)\]\{([^\}]*)\}\{([^\}]*)\}\{([^\}]*)\}", r"\\mtrefiii[\1?\2-\3-\4]{\\ttl{\2 \3 \4}}", content)

        # defi
        content = re.sub(r"\\defi\[([^\]]*)\]\{([^\}]*)\}", r"\\defi[\1]{\\ttl{\2}}", content)
        content = re.sub(r"\\defi\{([^\}]*)\}", r"\\defi[\1]{\\ttl{\1}}", content)
        # defii
        content = re.sub(r"\\defii\[([^\]]*)\]\{([^\}]*)\}\{([^\}]*)\}", r"\\defii[\1]{\\ttl{\2}}{\\ttl{\3}}", content)
        content = re.sub(r"\\defii\{([^\}]*)\}\{([^\}]*)\}", r"\\defii[\1-\2]{\\ttl{\1}}{\\ttl{\2}}", content)
        # defiii
        content = re.sub(r"\\defiii\[([^\]]*)\]\{([^\}]*)\}\{([^\}]*)\}\{([^\}]*)\}", r"\\defiii[\1]{\\ttl{\2}}{\\ttl{\3}}{\\ttl{\4}}", content)
        content = re.sub(r"\\defiii\{([^\}]*)\}\{([^\}]*)\}\{([^\}]*)\}", r"\\defiii[\1-\2-\3]{\\ttl{\1}}{\\ttl{\2}}{\\ttl{\3}}", content)


        def inner_supper(m):
            # Inner replacement function
            # Inserts the \ttl before any trailing whitespace.

            (sub_inner, n) = re.subn(r"([\n\f\t\v\s]+)$", r"}\1", m.group(1))
            if n == 0:
                sub_inner+="}"

            return r"\ttl{"+sub_inner+m.group(6)

        def supper(m):
            # Outer replacement function.
            toreplace = m.group(4)

            if re.match(r"^([\n\f\t\v\s]*)$", toreplace):
                # we are only whitespaces => do nothing
                pass
            else:
                # we are ntop only whitespaces => replace some sentences.
                toreplace = re.sub(r"(((\w)+\s+)*((\w)+\s*))([\.\!\?\,\;]?)", inner_supper, toreplace)
            return m.group(1)+toreplace+m.group(5)

        # All the text
        content = re.sub(r"((\]|\}|\$[^\$]*\$)(\w*))([^\\\{\}\$\]\[]+)(\s*)", supper, content)

        return match.group(1)+content+match.group(4)

    # Run it over viewnl and modnl environments
    content = re.sub(r"(\\begin{modnl})((.|\n)*)(\\end{modnl})", replacer, content)
    content = re.sub(r"(\\begin{viewnl})((.|\n)*)(\\end{viewnl})", replacer, content)

    try:
        write_file(newfn, content)
    except:
        err("Unable to write new module", newfn)
        return False

    std("Prepared translation of", modname, "from")
    std(orfn)
    std("to")
    std(newfn)
    std("Please finish the translation and then commit the module. ")

    return True
