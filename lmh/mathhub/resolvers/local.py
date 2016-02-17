from lmh.mathhub.resolvers import resolver
from lmh.external.programs import git

from fnmatch import fnmatch

import os, os.path

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

        repositories = set()

        # TODO: Scan the folder two levels deep
        groups = [name for name in os.listdir(self.__folder) if os.path.isdir(self.to_path(name))]

        for g in groups:
            for name in os.listdir(self.to_path(g)):
                fullpath = self.to_path(g, name)
                if os.path.isdir(fullpath) and self.__git.exists_local(fullpath):
                    repositories.add((g, name))

        return list(sorted(repositories))


    def match_repos(self, folder, spec):
        pass

    def match_repo(self, folder, spec):
        pass
