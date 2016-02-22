from lmh.mathhub.resolvers import resolver
from lmh.external.programs import git

from fnmatch import fnmatch

import os, os.path

from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class LocalMathHubResolver(resolver.MathHubResolver):
    """
    Represents a MathHubResolver() that can resolve local git repositories from
    a given folder.
    """

    def __init__(self, git_program, folder):
        """
        Creates a new LocalMathHubResolver() instance.

        Arguments:
            git_program
                Git() instance that is used to interface with git
        """
        if not isinstance(git_program, git.Git):
            raise TypeError("git_program needs to be a git.Git() instance. ")

        self.__git = git_program
        self.__folder = os.path.realpath(folder)
        self.__repos = None
    
    def can_answer_for(self, name):
        """
        If this function returns True that means this resolver can answer queries
        for the given instance name. For all other cases the behaviour is 
        unspecefied. 
        
        Arguments:
            name
                Name to check against
        Returns:
            A boolean indicating if this instance matches or not
        """
        
        return not self.from_path(name).startswith("..")

    def to_path(self, *paths):
        """
        Resolves a path relative to the root folder of this
        LocalMathHubResolver().

        Arguments:
            *paths
                Path components to resolve

        Returns:
            A string containing the resolved path
        """

        return os.path.join(self.__folder, *paths)
    
    def get_repo_path(self, group, name):
        """
        Gets the (full) path to a repository on disk. Never throws any 
        excpetions. Needs to return a path even if the repository does not
        yet exist locally. 

        Arguments:
            group
                The name of the group to find the repository.
            name
                Name of the repository to find.
        Returns:
                A String representing the path to the repository.
        """
        
        return self.to_path(group, name)

    def from_path(self, path, *prefixes):
        """
        Returns a path relative to the base path of this LocalMathHubResolver().

        Arguments:
            path
                Path to resolve
            prefixes
                Optional. Change the base path by calling to_path(prefixes)

        Returns:
            A string containing the resolved path
        """

        return os.path.relpath(os.path.realpath(path), self.to_path(*prefixes))

    def _resolve_group(self, group):
        """
        Private function used to resolve a group name.

        Arguments:
            group
        Returns:
            A string representing the resolved group name.
        """

        if not ("/" in group):
            return group
        else:
            return self.from_path(group)

    def _match_name(self, spec, group, name):
        """
        Private function used to check if a single name matches a specification.
        By default uses fnmatch.

        Arguments:
            spec
                Spec to check against
            group
                Group in which the name is to be resolved
            name
                Name of repository to check against
        """

        # match directly first
        if fnmatch(name, spec):
            return True

        # else go relatively to the root path
        else:
            return fnmatch('%s' % name, self.from_path(spec, group))

    def _match_full(self, spec, group, name):
        """
        Private function used to check if a full repository name matches a specification.
        By default uses fnmatch.

        Arguments:
            spec
                Spec to check against
            group
                Group of repository to check against
            name
                Name of repository to check against
        """

        # match directly first
        if fnmatch('%s/%s' % (group, name), spec):
            return True

        # else go relatively to the root path
        else:
            return fnmatch('%s/%s' % (group, name), self.from_path(spec))

    def get_all_repos(self):
        """
        Gets a (non-cached) list of repositories or throws NotImplementedError
        if not available. Should be overriden by the subclass.

        Returns:
            A list of pairs of strings (group, name) representing repositories.
        """
        
        if self.__repos != None:
            return self.__repos

        repositories = set()
        
        groups = [name for name in os.listdir(self.__folder) if os.path.isdir(self.to_path(name))]

        for g in groups:
            for name in os.listdir(self.to_path(g)):
                fullpath = self.to_path(g, name)
                if os.path.isdir(fullpath) and self.__git.exists_local(fullpath):
                    repositories.add((g, name))

        self.__repos = list(sorted(repositories))
        return self.__repos
    
    def repo_exists(self, group, name):
        """
        Checks if this Resolver can find the path to a repository. Should be 
        overriden by subclass for speed advantages. By default checks the output
        of get_all_repos(). 
        
        Arguments: 
            group
                Name of the group to check for repo. 
            name
                Name of the repository to check. 
        Returns:
            A boolean indicating if the repository exists or not. 
        """
        
        try:
            
            all_repos = self.get_all_repos()
            
            if (group, name) in all_repos:
                return True
        except exceptions.MathHubException:
            return False
    
    def clear_repo_cache(self):
        """
        Clears the cache of this Resolver. Should be implemented by the subclass. 
        """
        self.__repos = None
