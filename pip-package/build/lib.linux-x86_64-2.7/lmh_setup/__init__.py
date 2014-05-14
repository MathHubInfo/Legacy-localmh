import os
import sys
import subprocess
import argparse
import shutil
import signal
import imp

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def install_lmh(install, setupuri = "http://gl.mathhub.info/MathHub/localmh.git", branch=""):
    if not os.path.exists(install):
        os.makedirs(install)

    islinux = os.name == "posix"
    iswin = os.name == "nt"
    git = which("git")

    if git == None:
        print "Unable to locate the git executable. "
        print "Please make sure it is in the $PATH environment variable. "
        if islinux: 
          print "On a typical Ubuntu system you may install this with:"
          print "    sudo apt-get install git"
        if iswin:
          print "On Windows, you can install Git for Windows. Please see: "
          print "    http://msysgit.github.io/"
        return False
    if branch == "":
        subprocess.Popen([git, "clone", setupuri, install], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr).wait()
    else:
        subprocess.Popen([git, "clone", "-b", branch, setupuri, install], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr).wait()
    return True

def update_lmh(install, setupuri = "http://gl.mathhub.info/MathHub/localmh.git", branch=""):

    islinux = os.name == "posix"
    iswin = os.name == "nt"
    git = which("git")

    if git == None:
        print "Unable to locate the git executable. "
        print "Please make sure it is in the $PATH environment variable. "
        if islinux: 
          print "On a typical Ubuntu system you may install this with:"
          print "    sudo apt-get install git"
        if iswin:
          print "On Windows, you can install Git for Windows. Please see: "
          print "    http://msysgit.github.io/"
        return False
    if branch == "":
        subprocess.Popen([git, "remote", "add", "updater", setupuri], cwd=install, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr).wait()
        subprocess.Popen([git, "pull", "updater", "master"], cwd=install, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr).wait()
        subprocess.Popen([git, "remote", "rm", "updater"], cwd=install, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr).wait()
    else:
        subprocess.Popen([git, "remote", "add", "updater", setupuri], cwd=install, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr).wait()
        subprocess.Popen([git, "pull", "updater", branch], cwd=install, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr).wait()
        subprocess.Popen([git, "remote", "rm", "updater"], cwd=install, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr).wait()
    return True
def run_lmh(install):
    # run lmh
    s = imp.load_source("main", install + "/bin/lmh")

    # check if s has an attribute called main
    if hasattr(s, "main"):
        s.main()
    else:
        run_lmh_legacy(install)

    sys.exit(0)

def run_lmh_legacy(install):
    # run the legacy version of lmh
    try:
        args = [sys.executable, install + "/bin/lmh"] + sys.argv[1:]
        runner = subprocess.Popen(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    except:
        print "lmh core: Unable to run lmh. Please use the new version of lmh. "
        sys.exit(1)

    def do_the_run():
        try:
            runner.wait()
        except KeyboardInterrupt:
            runner.send_signal(signal.SIGINT)
            do_the_run()

    do_the_run()
    
    sys.exit(runner.returncode)

def has_lmh(install):
    return os.path.isfile(install + "/bin/lmh")

def run_core(args, install):
    parser = argparse.ArgumentParser(prog="lmh core")

    ins2 = parser.add_argument_group('Paths').add_mutually_exclusive_group()
    ins2.add_argument('-i', '--install-to', default="", help='Set install path. ')
    ins2.add_argument('-m', '--migrate-to', default="", help='Migrate existing installation to given path. ')
    ins2.add_argument('-u', '--use', default="", help='Use installation at the given path. ')

    ins3 = parser.add_argument_group('Actions').add_mutually_exclusive_group()
    ins3.add_argument('-in', '--install', action="store_const", const="in", dest="action", default="", help='Create a new instalation. ')
    ins3.add_argument('-up', '--upgrade-install', action="store_const", const="up", dest="action", help='Upgrade installation in place. ')
    ins3.add_argument('-rm', '--remove-install', action="store_const", const="rm", dest="action", help='Remove existing installation including all installed repositories. ')
    
    ins4 = parser.add_argument_group('Core sources')
    ins4.add_argument('-s', '--source', metavar="source@branch", default="", help='Set source to get repository from. ')

    info = parser.add_argument_group('Information').add_mutually_exclusive_group()
    info.add_argument('-pc', '--print-core-path', dest="pc", action="store_const", const=True, default=False, help='Print path of the core script and exit. ')
    info.add_argument('-pi', '--print-installed-path', dest="pi", action="store_const", const=True, default=False, help='Print path of the installed user scripts and exit. ')
    info.add_argument('-pg', '--print-git-path', dest="pg", action="store_const", const=True, default=False, help='Print path of the git used and exit. ')

    args = parser.parse_args(args)

    if args.pc:
        print __file__
        return
    if args.pi:
        print install
        return
    if args.pg:
        print which("git")
        return

    # Parse source
    core_source = "http://gl.mathhub.info/MathHub/localmh.git"
    core_branch = ""

    if not args.source == "":
        index = args.source.find("@")
        if index == 0:
          core_branch = args.source[1:]
        elif index > 0:
          core_source = args.source[:index]
          core_branch = args.source[index+1:]
        else:
          core_source = args.source

        print "Using Core Version: "+core_source+"@"+core_branch


    new = "install"

    # Figure out what to use
    if args.install_to != "":
        install = os.path.expanduser(args.install_to)
        try:
            text_file = open(os.path.expanduser("~/.lmhpath"), "w")
            text_file.write(install)
            text_file.close()
        except:
            print "Warning: Unable to store new location in ~/.lmhpath. Please fix this manually. "
    if args.migrate_to != "":
        to = os.path.expanduser(args.install_to)
        if not has_lmh(install):
            print "Error: No Installation exists at '"+install+"'"
            print "Unable to migrate installation. "
            return
        print "Migrating installation from "
        print "'"+install+"' to '"+to+"' ..."
        try:
            shutil.move(install, to)
        except:
            print "Unable to migrate installation, please attempt reinstalling. "
            return
        try:
            text_file = open(os.path.expanduser("~/.lmhpath"), "w")
            text_file.write(to)
            text_file.close()
        except:
            print "Warning: Unable to store new location in ~/.lmhpath. Please fix this manually. "

        install = to        
        print "Done. "

        new = "skip"

    elif args.use != "":
        to = os.path.expanduser(args.use)

        try:
            text_file = open(os.path.expanduser("~/.lmhpath"), "w")
            text_file.write(to)
            text_file.close()
        except:
            print "Warning: Unable to store new location in ~/.lmhpath. Please fix this manually. "

        install = to
        new = "skip"

    action = ""

    if args.action == "in":
        action = "install"
    elif args.action == "up":
        action = "update"
    elif args.action == "rm":
        action = "remove"
    elif new != "skip":
        action = "install"

    print "Local directory: '"+install+"'"

    if action == "install":
        if has_lmh(install):
            print "Error: Installation already exists at '"+install+"'"
            print "Consider using --upgrade-install. "
            return
        print "Installing lmh ..."
        install_lmh(install, setupuri = core_source, branch = core_branch)
        print "Done. "

    if action == "update":
        if not has_lmh(install):
            print "Error: No installation exists at '"+install+"'"
            print "Unable to update installation"
            return
        print "Updating lmh ..."
        update_lmh(install, setupuri = core_source, branch = core_branch)
        print "Done. "

    if action == "remove":
        if not has_lmh(install):
            print "Error: No installation exists at '"+install+"'"
            print "Can not remove. "
            return

        print "Removing lmh ..."
        try:
            shutil.rmtree(install)
        except:
            print "Unable to remove installation, please remove '"+install+"' manually. " 
        print "Done. "

def get_lmh_path():
    content = ""
    try:
        f = open(os.path.expanduser("~/.lmhpath"), 'r')
        content = f.readlines()[0]
    except:
        pass
    finally:
        try:
            f.close()
        except:
            pass
    if content:
        return os.path.expanduser(content)
    else:
        return os.path.expanduser("~/localmh")

def main():
    install = get_lmh_path()
    if len(sys.argv) >= 2 and sys.argv[1] == "core":
        run_core(sys.argv[2:], install)
    else:
        if not has_lmh(install):
            print "No installed version of lmh found ..."
            print "Installing lmh now ..."
            if not install_lmh(install):
                print "Unable to install lmh ..."
                return

        run_lmh(install)