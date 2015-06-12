from lmh import main

def do(args, unknown):
    res = True

    if args.mode == "all" or args.mode == "self":
        res = res and main(["selfupdate"])
    if args.mode == "all" or args.mode == "build":
        res = res and main(["update-build"])
    if args.mode == "all" or args.mode == "external":
        res = res and main(["setup", "--update"])


    return res
