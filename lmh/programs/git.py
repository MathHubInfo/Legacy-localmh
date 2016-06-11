import os
import os.path
import subprocess
import sys

from lmh.programs import program
from lmh.utils.caseclass import caseclass

@caseclass
class Git(program.Program):
    """
    Represents an interface to git.
    """
    def __init__(self, systems_dir, sty_dir, git_executable = "git"):
        """
        Creates a new Git() instance.

        Arguments:
            git_executable
                Optional. Name of the git executable. Defaults to "git".
            systems_dir
                Directory to find systems in
            sty_dir
                Directory to find sty files in
        """
        
        self.__encoding = "utf-8" # TODO: We might not want to hardcode
        self.__executable = git_executable
        
        super(Git, self).__init__(systems_dir, sty_dir)

    #
    # GENERAL commands
    #

    def __do__(self, dest, cmd, *args, **kwargs):
        """
        Performs an arbitrary git command and returns a proc handle

        Arguments:
            cmd
                Git command to run
            dest
                Directory to run command in
            *args
                Optional arguments to pass to the command
            **kwargs
                Optional arguments to pass to subprocess.Popen

        Returns:
            A subprocess.Popen handle
        """
        
        try:
            return self._popen(self.__executable, cmd, *args, cwd=dest, **kwargs)
        except program.ExecutableNotFound:
            raise GitNotFound()

    def do(self, dest, cmd, *args):
        """
        Performs an arbitrary git command and returns if the command succeeded.

        Arguments:
            cmd
                Git command to run
            dest
                Directory to run command in
            *args
                Optional arguments to pass to the command

        Returns:
            A boolean indicating if the return code of the command was 0 or not
        """
        proc = self.__do__(dest, cmd, *args, stderr=sys.stderr, stdout=sys.stdout)
        proc.wait()

        return (proc.returncode == 0)

    def do_quiet(self, dest, cmd, *args):
        """
        Same as do() but surpresses any output from the command
        """

        proc = self.__do__(dest, cmd, *args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.wait()

        return (proc.returncode == 0)

    def do_data(self, dest, cmd, *args):
        """
        Same as do() but instead of returning a boolean returns a pair of
        strings representing stdout and stderr output of the command.
        """

        proc = self.__do__(dest, cmd, *args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.wait()

        data = proc.communicate()

        return (data[0].decode(self.__encoding), data[1].decode(self.__encoding))

    #
    # SIMPLE ALIASES
    #

    def clone(self, dest, *args):
        """
        Clones a git repository to a given folder.

        Arguments:
            dest
                Folder to clone repository to
            *arg
                Optional arguments to pass to the git clone command

        Returns:
            A boolean indicating if the return code of the git clone command
            was 0 or not
        """
        return self.do(dest, "clone", *args)

    def pull(self, dest, *args):
        """
        Pulls a git repository.

        Arguments:
            dest
                Folder to pull repository in
            *arg
                Optional arguments to pass to the git clone command

        Returns:
            A boolean indicating if the return code of the git pull command
            was 0 or not
        """
        return self.do(dest, "pull", *args)

    def commit(self, dest, *args):
        """
        Commits a git repository.

        Arguments:
            dest
                repository to commit
            *arg
                Optional arguments to pass to the git commit command

        Returns:
            A boolean indicating if the return code of the git commit command
            was 0 or not
        """

        return self.do(dest, "commit", *args)


    def push(self, dest, *args):
        """
        Pushes a git repository.

        Arguments:
            dest
                repository to push
            *args
                Optional arguments to pass to the git push command

        Returns:
            A boolean indicating if the return code of the git push command
            was 0 or not
        """

        return self.do(dest, "push", *args)

    def status(self, dest, *args):
        """
        Runs git status on a git repository.

        Arguments:
            dest
                repository to status
            *args
                Optional arguments to pass to the git status command

        Returns:
            A boolean indicating if the return code of the git status command
            was 0 or not
        """

        return self.do(dest, "status", *args)

    def status_message(dest, *arg):
        """
        Runs git status and returns the status message or None

        Arguments:
            dest
                repository to run git status in
            *args
                Optional arguments to pass to the git status command

        Returns:
            A string containing the status message or None
        """

        proc = self.__do__(dest, "status", *args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.wait()

        data = proc.communicate()

        if proc.returncode != 0:
            return None
        else:
            return data[0].decode(self.__encoding)
    #
    # SPECIFIC COMMANDS (non-standard)
    #
    def exists_remote(self, dest, askpass=False):
        """
        Checks if a remote git repository exists

        Arguments:
            dest
                remote repository to check
            askpass
                Optional. If set to True enables asking for passwords.

        Returns:
            A boolean indicating if the remote repository exists or not.
        """

        env = os.environ.copy()
        if not askpass:
            env["GIT_TERMINAL_PROMPT"] = "0"
            env["GIT_ASKPASS"] = "/bin/echo"

        proc = self.__do__(os.getcwd(), "ls-remote", dest, env=env, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.wait()

        return proc.returncode == 0

    def exists_local(self, dest, askpass=False):
        """
        Checks if a local git repository exists

        Arguments:
            dest
                local repository to check

        Returns:
            A boolean indicating if the local repository exists or not.
        """

        return self.do_quiet(dest, "rev-parse")
    
    def get_remote_status(self, dest):
        """
        Gets the status of a remote repository in dest
        
        Arguments:
            dest
                Folder to find repository in
        Returns:
             one of 'ok', 'pull', 'push', 'divergence' or None indicating the
             status of the remote
        """
        
        # update the remote status
        if not self.do_quiet(dest, 'remote', 'update'):
            return None
        
        # figure out my current branch
        my_branch = self.do_data(dest, 'rev-parse', '--abbrev-ref', 'HEAD')[0].split('\n')[0]
        
        # figure out the upstream branch
        my_upstream = self.do_data(dest, 'symbolic-ref', '--abbrev-ref', 'HEAD')[0].split('\n')[0]
        my_upstream = self.do_data(dest, 'for-each-ref', '--format=%(upstream:short)', my_upstream)[0].split('\n')[0]
        
        # find local and remote hashes
        local = self.do_data(dest, 'rev-parse', my_branch)[0].split('\n')[0]
        remote = self.do_data(dest, 'rev-parse', my_upstream)[0].split('\n')[0]
        
        # as well as the merge base
        base = self.do_data(where, 'merge-base', my_branch, my_upstream)[0].split('\n')[0]

        if local == remote:
            return 'ok'
        elif local == base:
            return 'pull'
        elif remote == base:
            return 'push'
        else:
            return 'divergence'
    
    def make_orphan_branch(self, dest, name):
        """
        Makes an orphaned branch. 
        
        Arguments:
            dest
                Git repository to create branch in
            name
                Name of the branch
        
        Returns:
            a boolean indicating if creation was successfull. 
        """
        
        # true | git mktree
        proc = self.__do__(dest, 'mktree', stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        treeid = proc.communicate(input=b'')[0].decode('utf-8').rstrip("\n")
        proc.wait()
        
        if proc.returncode != 0:
            return False
        
        # ... | xargs git commit-tree
        proc = self.__do__(dest, 'commit-tree', treeid, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        commid = proc.communicate(input=b'')[0].decode('utf-8').rstrip("\n")
        proc.wait()
        
        if proc.returncode != 0:
            return False
        
        # ... | xargs git branch $name
        proc = self.__do__(dest, 'branch', name, commid, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        res = proc.communicate(input=b'')[0].decode('utf-8').rstrip("\n")
        proc.wait()

        return proc.returncode == 0

class GitNotFound(program.ExecutableNotFound):
    """
    Exception that is thrown when git is not found
    """
    
    def __init__(self):
        super(GitNotFound, self).__init__("Can not find git")
