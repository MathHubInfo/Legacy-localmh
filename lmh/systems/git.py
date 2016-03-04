from lmh.systems import system

import os
import shutil

class GitBasedSystem(system.System):
    """
    Represents a system managed by Git
    """
    
    def __init__(self, name, source, branch = None, base = None):
        """
        Creates a new GitBasedSystem() instance. 
        
        Arguments:
            name
                Name of the system to create
            base
                Base directory to install system in. 
            source
                Git source to get system from
            branch
                Git branch (or REFSPEC) to get system from
        """
        
        super(GitBasedSystem, self).__init__(name, base = base)
        
        self.__source = source
        self.__branch = branch
    
    @property
    def git(self):
        """
        Gets the git program to be used by this GitBasedSystem
        
        Returns:
            a git() instance
        """
        
        return self.manager('git')
    
    def _install(self):
        """
        Protected Function used to install this system. Should be overridden by subclass.  
        
        Returns:
            a boolean indicating if installation was successfull. 
        """
        
        if self.__branch != None:
            return self.git.clone(self.base, self.source, '-b', self.__branch)
        else:
            return self.git.clone(self.base, self.source)
    
    def _update(self):
        """
        Protected Function used to update this system. Should be overridden by subclass.  
        
        Returns:
            a boolean indicating if update was successfull. 
        """
        
        return self.git.pull(self.base)