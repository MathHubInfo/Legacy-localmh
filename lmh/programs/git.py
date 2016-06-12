from typing import List, Dict, Any, Tuple, Optional

import os
import os.path
import subprocess
import sys

from lmh.programs import program
from lmh.utils.caseclass import caseclass


@caseclass
class Git(program.Program):
    """ Represents an interface to git. """

    def __init__(self, systems_dir: str, sty_dir: str, git_executable: str = "git"):
        """ Creates a new Git() instance.

        :param systems_dir: Directory to find systems in.
        :param sty_dir: Directory to find sty files in.
        :param git_executable: Path to the Git Executable to use. Defaults to "git".
        """

        # TODO: We might not want to hard-code the encoding
        self.__encoding = "utf-8"  # type: str
        self.__executable = git_executable  # type: str
        
        super(Git, self).__init__(systems_dir, sty_dir)

    #
    # GENERAL commands
    #

    def __do__(self, dest: str, cmd: str, *args: List[str], **kwargs: Dict[str, Any]) -> subprocess.Popen:
        """ Performs an arbitrary git command and returns subprocess.Popen handle.

        :param cmd: Git command to run.
        :param dest: Directory to run command in.
        :param args: Optional arguments to pass to the command.
        :param kwargs: Optional arguments to pass to subprocess.Popen.
        """
        
        try:
            return self._popen(self.__executable, cmd, *args, cwd=dest, **kwargs)
        except program.ExecutableNotFound:
            raise GitNotFound()

    def do(self, dest: str, cmd: str, *args: List[str]) -> bool:
        """ Performs an arbitrary git command and returns if the command succeeded.

        :param cmd: Git command to run.
        :param dest: Directory to run command in.
        :param args: Optional arguments to pass to the command.
        """

        proc = self.__do__(dest, cmd, *args, stderr=sys.stderr, stdout=sys.stdout)
        proc.wait()

        return proc.returncode == 0

    def do_quiet(self, dest, cmd, *args) -> bool:
        """ Same as do() but suppresses command output. """

        proc = self.__do__(dest, cmd, *args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.wait()

        return proc.returncode == 0

    def do_data(self, dest, cmd, *args) -> Tuple[str, str]:
        """ Same as do() but instead of returning a boolean returns a pair of strings representing STDOUT and STDERR
        output of the command.
        """

        proc = self.__do__(dest, cmd, *args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.wait()

        data = proc.communicate()

        return data[0].decode(self.__encoding), data[1].decode(self.__encoding)

    #
    # SIMPLE ALIASES
    #

    def clone(self, dest: str, *args: List[str]) -> bool:
        """ Clones a git repository to a given folder and returns if the command succeeded.

        :param dest: Folder to clone repository to.
        :param arg: Optional arguments to pass to the git clone command.
        """

        return self.do(dest, "clone", *args)

    def pull(self, dest: str, *args: List[str]) -> bool:
        """ Pulls a git repository and returns if the command succeeded.

        :param dest: Folder to pull repository in.
        :param args: Optional arguments to pass to the git pull command.
        """

        return self.do(dest, "pull", *args)

    def commit(self, dest: str, *args: List[str]) -> bool:
        """Commits a git repository and returns if the command succeeded.

        :param dest: repository to commit
        :param args: Optional arguments to pass to the git commit command.
        """

        return self.do(dest, "commit", *args)

    def push(self, dest: str, *args: List[str]) -> bool:
        """ Pushes a git repository and returns if the command succeeded.

        :param dest: Folder to push repository in.
        :param args: Optional arguments to pass to the git push command.
        """

        return self.do(dest, "push", *args)

    def status(self, dest: str, *args: List[str]) -> bool:
        """ Runs git status on a git repository and returns if the command succeeded.

        :param dest: Folder to run git status in.
        :param args: Optional arguments to pass to the git status command.
        """

        return self.do(dest, "status", *args)

    def status_message(self, dest: str, *args: List[str]) -> Optional[str]:
        """ Runs git status on a git repository and retuns the status message or None.

        :param dest: Folder to run git status in.
        :param args: Optional arguments to pass to the git status command.
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

    def exists_remote(self, dest: str, ask_pass: bool=False) -> bool:
        """ Checks if a remote git repository exists.

        :param dest: Remote repository to check.
        :param ask_pass: Optional. If set to True enables asking for passwords.
        """

        # disable asking for passwords if configured
        env = os.environ.copy()
        if not ask_pass:
            env["GIT_TERMINAL_PROMPT"] = "0"
            env["GIT_ASKPASS"] = "/bin/echo"

        proc = self.__do__(os.getcwd(), "ls-remote", dest, env=env, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.wait()

        return proc.returncode == 0

    def exists_local(self, dest: str) -> bool:
        """ Checks if a local git repository exists.

        :param dest: Local repository to check.
        """

        return self.do_quiet(dest, "rev-parse")

    # TODO: Migrate these to integers to be nicer
    UP_TO_DATE = "ok"
    REMOTE_AHEAD = "pull"
    LOCAL_AHEAD = "push"
    DIVERGENCE = "divergence"

    def get_remote_status(self, dest: str) -> str:
        """ Gets the status of a remote repository in dest as compared to the local one.

        :param dest: Folder to find repository in.
        :return: One of the constants Git.UP_TO_DATE, Git.REMOTE_AHEAD, Git.LOCAL_AHEAD, Git.DIVERGENCE
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
        base = self.do_data(dest, 'merge-base', my_branch, my_upstream)[0].split('\n')[0]

        # and then return the appropriate constant
        if local == remote:
            return Git.UP_TO_DATE
        elif local == base:
            return Git.REMOTE_AHEAD
        elif remote == base:
            return Git.LOCAL_AHEAD
        else:
            return Git.DIVERGENCE
    
    def make_orphan_branch(self, dest: str, name: str) -> bool:
        """ Creates an orphaned branch and returns a boolean indicating if creation was successfull.

        :param dest: Git repository to create orphaned branch in.
        :param name: Name of branch to create.
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
    """ Exception that is thrown when git is not found. """
    
    def __init__(self):
        """ Creates a new GitNotFound() instance. """
        super(GitNotFound, self).__init__("Can not find git")
