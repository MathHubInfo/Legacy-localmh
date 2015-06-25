import os
import re
from lmh.lib.io import err
from lmh.lib.modules.translate import transmod

def do(args, unknown):
    ret = True

    multiregex = r"(.*)\.(.*)\.tex"

    args.source = args.source[0]

    try:
        ofn = os.path.abspath(args.source)
        ofn = re.findall(multiregex, ofn)[0]
    except:
        err("Module", args.source, "does not seem to be multi-lingual. ")
        err("(Can not extract language from filename. )")
        err("Please rename it to <module>.<language>.tex and try again. ")
        return False

    if not os.path.isfile(os.path.abspath(args.source)):
        err("File", args.source, " does not exist. ")
        return False

    for lang in args.dest:
        langfn = ofn[0]+"."+lang+".tex"
        if not args.force and os.path.isfile(langfn):
            err("File", langfn, "exists, skipping. ")
            err("Use --force to overwrite. ")
            ret = False
            continue

        ret = transmod(ofn[0], ofn[1], lang, pre_terms = args.terms) and ret

    return ret
