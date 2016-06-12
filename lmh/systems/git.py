from typing import Optional

from lmh.systems import system
from lmh.programs.git import Git


class GitBasedSystem(system.System):
    """ Represents a system managed by Git. """
    
    def __init__(self, name: str, source: str, branch: Optional[str] = None, base: Optional[str] = None):
        """ Creates a new GitBasedSystem() instance.

        :param name: Name of the system to create.
        :param source: Git source to get system from.
        :param branch: Optional. Git branch (or REFSPEC) to get system from.
        :param base: Base directory to install system in.
        """
        
        super(GitBasedSystem, self).__init__(name, base=base)
        
        self.__source = source  # type: str
        self.__branch = branch  # type: Optional[str]
    
    @property
    def git(self) -> Git:
        """ Gets the git program to be used by this GitBasedSystem. """
        
        return self.manager('git')

    @property
    def source(self) -> str:
        """ Returns the Git source to get system from. """

        return self.__source

    @property
    def branch(self) -> str:
        """ Gets the git branch (or REFSPEC) to get system from. """

        return "HEAD" if self.__branch is None else self.__branch
    
    def _install(self) -> bool:
        """ Protected Function used to install this system. """
        
        if self.branch != "HEAD":
            return self.git.clone(self.base, self.source, '-b', self.__branch)
        else:
            return self.git.clone(self.base, self.source)
    
    def _update(self) -> bool:
        """ Protected Function used to update this system. """
        
        return self.git.pull(self.base)