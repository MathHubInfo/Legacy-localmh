import sys
import os.path
import subprocess

from lmh.lib.extenv import git_executable


def clone(dest, *arg):
    """Clones a git repository. """
    args = [git_executable, "clone"]
    args.extend(arg)
    proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)
    proc.wait()
    return (proc.returncode == 0)

def pull(dest, *arg):
    """Pulls a git repository. """

    args = [git_executable, "pull"]
    args.extend(arg)
    proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)
    proc.wait()
    return (proc.returncode == 0)

def commit(dest, *arg):
    """Commits a git repository. """
    args = [git_executable, "commit"]
    args.extend(arg)
    proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)
    proc.wait()
    return (proc.returncode == 0)

def push(dest, *arg):
    """Pulls a git repository. """

    args = [git_executable, "push"]
    args.extend(arg);
    proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)
    proc.wait()
    return (proc.returncode == 0)

def do(dest, cmd, *arg):
    """Does an arbitrary git command and returns if it suceeded. """

    args = [git_executable, cmd]
    args.extend(arg)
    proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)
    proc.wait()
    return (proc.returncode == 0)

def do_quiet(dest, cmd, *arg):
    """Does an arbitrary git command quietly and returns if it suceeded. """

    args = [git_executable, cmd]
    args.extend(arg)
    proc = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=dest)
    proc.wait()
    return (proc.returncode == 0)

def do_data(dest, cmd, *arg):
    """Does an arbitrary git command and return stdout and sterr. """

    args = [git_executable, cmd]
    args.extend(arg)
    proc = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=dest)
    proc.wait()
    return proc.communicate()

def status(dest, *arg):
    """Runs git status and returns the status message. """

    args = [git_executable, "status"];
    args.extend(arg)
    proc = subprocess.Popen(args, stderr=sys.stderr, stdout=subprocess.PIPE, cwd=dest)
    proc.wait()
    if(proc.returncode == 0):
        return proc.communicate()[0]
    else:
        return False
def status_pipe(dest, *arg):
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
    if not do_quiet(where, "remote", "update"):
        return "failed"

    # Figure out my branch
    my_branch = do_data(where, "rev-parse", "--abbrev-ref", "HEAD")[0].split("\n")[0]
    # And the upstream url
    my_upstream = do_data(where, "symbolic-ref", "-q", "HEAD")[0].split("\n")[0]
    my_upstream = do_data(where, "for-each-ref", "--format=%(upstream:short)", my_upstream)[0].split("\n")[0]

    # Turn it into hashes
    local = do_data(where, "rev-parse", my_branch)
    remote = do_data(where, "rev-parse", my_upstream)
    base = do_data(where, "merge-base", my_branch, my_upstream)

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
