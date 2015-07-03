import os

from lmh.lib import setnice
from lmh.lib.io import std, err

import lmh.lib.modules.generators
from lmh.lib.modules import resolve_pathspec


def do(args, unknown):
    if args.grep_log != None:
        args.update = "grep_log"


    # Make sure we are nice
    if args.nice != 0:
        setnice(args.nice)

    # We should be verbose and run simulate
    if args.verbose:
        args.quiet = True

    # if we are piping pdf log, we need to be quiet and single.
    try:
        if args.pdf_pipe_log:
            args.quiet = True
            args.workers = 1
    except:
        pass

    # When we have nothing to do
    # TODO: Make a joke
    if not args.pdf and not args.omdoc and not args.sms and not args.list and not args.localpaths and not args.alltex and not args.xhtml:
        if not args.quiet:
            std("Nothing to do ...")
        return True

    # Find all the modules
    try:
        if not args.quiet:
            std("Checking modules, this may take a while ...")
        modules = resolve_pathspec(args)
        if not args.quiet:
            std("Found", len(modules), "paths to work on. ")
    except KeyboardInterrupt:
        err("<<KeyboardInterrupt>>")
        return False

    # We want to list all the files
    if args.list:
        for m in modules:
            if m["type"] == "file":
                std(os.path.relpath(m["file"], "."))
        return True

    # Implications to set
    if args.xhtml and not args.skip_implies:
        args.omdoc = True

    if (args.pdf or args.xhtml) and not args.skip_implies:
        args.sms = True
        args.localpaths = True
        args.alltex = True

    # SMS Generation
    if args.sms:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.sms, args.grep_log)
        if not args.quiet:
            std("SMS: Generated", len(d), "file(s), failed", len(f), "file(s). ")
        if not res:
            if not args.quiet:
                err("SMS: Generation failed, skipping further generation. ")
            return False


    if args.localpaths and not args.list:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.localpaths, args.grep_log)
        if not args.quiet:
            std("LOCALPATHS: Generated", len(d), "file(s), failed", len(f), "file(s). ")
        if not res:
            if not args.quiet:
                err("LOCALPATHS: Generation failed, skipping further generation. ")
            return False

    if args.alltex and not args.list:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.alltex, args.grep_log)
        if not args.quiet:
            std("ALLTEX: Generated", len(d), "file(s), failed", len(f), "file(s). ")
        if not res:
            if not args.quiet:
                err("ALLTEX: Generation failed, skipping further generation. ")
            return False

    if args.omdoc:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.omdoc, args.grep_log)
        if not args.quiet:
            std("OMDOC: Generated", len(d), "file(s), failed", len(f), "file(s). ")
        if not res:
            if not args.quiet:
                err("OMDOC: Generation failed, skipping further generation. ")
            return False

    if args.pdf:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.pdf, args.grep_log, add_bd=args.pdf_add_begin_document, pdf_pipe_log=args.pdf_pipe_log)
        if not args.quiet:
            std("PDF: Generated", len(d), "file(s), failed", len(f), "file(s). ")
        if not res:
            if not args.quiet:
                err("PDF: Generation failed, skipping further generation. ")
            return False

    if args.xhtml:
        (res, d, f) = lmh.lib.modules.generators.run(modules, args.verbose, args.update, args.quiet, args.workers, lmh.lib.modules.generators.xhtml, args.grep_log)
        if not args.quiet:
            std("XHTML: Generated", len(d), "file(s), failed", len(f), "file(s). ")
            std("XHTML: Generation log may contain false positives, to be sure please check manually. ")
        if not res:
            if not args.quiet:
                err("XHTML: Generation failed, skipping further generation. ")
            return False


    return True
