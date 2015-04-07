import sys
import os.path
import subprocess

from lmh.lib.extenv import git_executable

# TODO: Do we want to make this a class?
# It might make things nicer.

# TODO: Prefix everything with git_

#
# BASIC METHODS
#

def git_do(dest, cmd, *arg):
    """
        Does an arbitrary git command and returns if it suceeded.

        @param dest Destination directory.
        @param cmd Commands to run.
        @param arg Arguments to use.

        @returns if the command ran sucessfully.
    """

    # assemble the command
    args = [git_executable, cmd]
    args.extend(arg)

    # It's gonna be a legen ...
    proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)

    # wait for it
    proc.wait()

    # ...dary return code.
    return (proc.returncode == 0)

def __do_quiet(dest, cmd, *arg):
    """
        Does an arbitrary git command quietly and returns the proc object.
        FOR INTERNAL USE ONLY.

        @param dest Destination directory.
        @param cmd Commands to run.
        @param arg Arguments to use.

        @returns the used proc object
    """

    # assemble the command
    args = [git_executable, cmd]
    args.extend(arg)

    # It's gonna be a legen ...
    proc = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=dest)

    # wait for it
    proc.wait()

    # ... dary process
    return proc

def git_do_data(dest, cmd, *arg):
    """
        Does an arbitrary git command quietly and returns the input and output text.

        @param dest Destination directory.
        @param cmd Commands to run.
        @param arg Arguments to use.

        @returns the data
    """
    # assemble the command.
    args = [git_executable, cmd]
    args.extend(arg)

    # run it
    proc = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=dest)

    # wait for it
    proc.wait()

    # and return the data sent.
    return proc.communicate()

#
# BASIC OPERATIONS
#

def clone(dest, *arg):
    """
        Does an arbitrary git command quietly and returns the proc object.
        FOR INTERNAL USE ONLY.

        @param dest Destination directory.
        @param cmd Commands to run.
        @param arg Arguments to use.

        @returns the used proc object
    """
    """Clones a git repository. """
    return git_do(dest, "clone", *args)

def push(dest, *arg):
    """Pushes a git repository. """
    return git_do(dest, "push", *args)

def pull(dest, *arg):
    """Pulls a git repository. """
    return git_do(dest, "pull", *args)

def commit(dest, *arg):
    """Commits a git repository. """
    return git_do(dest, "commit", *args)

def status(dest, *arg):
    """Runs git status and pipes output. """

    args = [git_executable, "status"];
    args.extend(arg)
    proc = subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr, cwd=dest)
    proc.wait()
    if(proc.returncode == 0):
        return True
    else:
        return False

def exists(dest):
    """Checks if a git repository exists. """
    args = [git_executable, "ls-remote", dest]
    proc = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.wait()
    return (proc.returncode == 0)

def is_repo(dest):
    """Checks if a git repository exists (locally) """
    # Checks if something
    args = [git_executable, "rev-parse", dest]
    proc = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.wait()

    if (proc.returncode == 0):
        return os.path.abspath(root_dir(dest)) == os.path.abspath(dest)
    else:
        return False

def root_dir(dir = "."):
    """Finds the git root dir of the given path. """

    if os.path.isfile(dir):
        dir = os.path.dirname(dir)

    rootdir = subprocess.Popen([git_executable, "rev-parse", "--show-toplevel"],
                                                            stdout=subprocess.PIPE,
                                                            cwd=dir,
                                                            ).communicate()[0]
    rootdir = rootdir.strip()
    return rootdir

def is_tracked(file):
    f = os.path.abspath(file)
    p = os.path.dirname(f)

    args = [git_executable, "ls-files", f, "--error-unmatch"]
    proc = subprocess.Popen(args, cwd=p, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.wait()
    return (proc.returncode == 0)

def get_remote_status(where):
    # quietly make an update with the remote
    if __do_quiet(where, "remote", "update").returncode != 0:
        return "failed"

    # Figure out my branch
    my_branch = git_do_data(where, "rev-parse", "--abbrev-ref", "HEAD")[0].split("\n")[0]
    # And the upstream url
    my_upstream = git_do_data(where, "symbolic-ref", "-q", "HEAD")[0].split("\n")[0]
    my_upstream = git_do_data(where, "for-each-ref", "--format=%(upstream:short)", my_upstream)[0].split("\n")[0]

    # Turn it into hashes
    local = git_do_data(where, "rev-parse", my_branch)
    remote = git_do_data(where, "rev-parse", my_upstream)
    base = git_do_data(where, "merge-base", my_branch, my_upstream)

    if local == remote:
        return "ok"
    elif local == base:
        return "pull"
    elif remote == base:
        return "push"
    else:
        return "divergence"

def origin(dir="."):
    """Finds the origin of a given git repository. """

    return subprocess.Popen([git_executable, "remote", "show", "origin", "-n"],
                                                    stdout=subprocess.PIPE,
                                                    cwd=dir,
                                                    ).communicate()[0]
