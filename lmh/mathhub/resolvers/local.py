from typing import Optional, List, Tuple

import os
import os.path
from fnmatch import fnmatch

from lmh.programs.git import Git

from lmh.mathhub.resolvers import resolver
from lmh.utils.caseclass import caseclass
from lmh.utils import exceptions


@caseclass
class LocalMathHubResolver(resolver.MathHubResolver):
    """ Represents a MathHubResolver() that can resolve local git repositories from a given folder. """

    def __init__(self, git_program: Git, root: str):
        """ Creates a new LocalMathHubResolver() instance.

        :param git_program: Git Instance used in this local MathHubResolver.
        :param root: Root Folder to resolve repositories relative to.
        """

        self.__git = git_program  # type: Git
        self.__root = os.path.realpath(root)  # type: str
        self.__repos = None  # type: Optional[List[str]]

    @property
    def root(self) -> str:
        """ Returns the root path of this LocalMathHubResolver. """

        return self.__root

    def to_path(self, *paths: List[str]) -> str:
        """ Resolves a path relative to the root folder of this LocalMathHubResolver().

        :param paths: Path components to resolve.
        """

        return os.path.join(self.root, *paths)

    def from_path(self, path: str, *prefixes: List[str]) -> str:
        """ Returns a path relative to the base path of this LocalMathHubResolver().

        :param path: Path to start with.
        :param prefixes: Optional. Change the base path by calling to_path(*prefixes).
        """

        return os.path.relpath(os.path.realpath(path), self.to_path(*prefixes))

    def can_answer_for(self, name: str) -> bool:
        """ Performs a partial check if this resolver can answer queries for the given instance name. If this method
        returns true, the MathHubResolver can answer queries, for all other cases the behaviour is unspecified.

        :param name: Name to check.
        """
        
        return not self.from_path(name).startswith("..")
    
    def get_repo_path(self, group: str, name: str) -> str:
        """Gets the full path to a repository or throws NotImplementedError. May also throw RepositoryNotFound.

        :param group: Group of repository to resolve.
        :param name: Name of repository to resolve.
        """
        
        return self.to_path(group, name)

    def _resolve_group(self, group: str) -> str:
        """ Protected function used to resolve a group name. By default does nothing.

        :param group: Group name to resolve.
        """

        if not ("/" in group):
            return group
        else:
            return self.from_path(group)

    def _match_name(self, spec: str, group: str, name: str) -> bool:
        """ Protected function used to check if a single name matches a specification.

        :param spec: Spec to check against.
        :param group: Group in which the name is to be resolved.
        :param name: Name of repository to check against
        """

        # match directly first
        if fnmatch(name, spec):
            return True

        # else go relatively to the root path
        else:
            return fnmatch('%s' % name, self.from_path(spec, group))

    def _match_full(self, spec: str, group: str, name: str) -> bool:
        """
        Protected function used to check if a full repository name matches a specification.

        :param spec: Spec to check against.
        :param group: Group of repository to check against.
        :param name: Name of repository to check against.
        """

        # match directly first
        if fnmatch('%s/%s' % (group, name), spec):
            return True

        # else go relatively to the root path
        else:
            return fnmatch('%s/%s' % (group, name), self.from_path(spec))

    def get_all_repos(self) -> List[Tuple[str, str]]:
        """ Gets a (possibly cached) list of repositories or throws NotImplementedError if not available.

        :return: A list of pairs of strings (group, name) representing repositories.
        """

        # fill the cache
        if self.__repos is None:
            self.__repos = self._get_all_repos()

        # return it
        return self.__repos

    def clear_repo_cache(self) -> None:
        """ Clears the cache of this Resolver. """

        self.__repos = None

    def _get_all_repos(self) -> List[Tuple[str, str]]:
        """ Gets a non-cached list of repositories or throws NotImplementedError if not available.

        :return: A list of pairs of strings (group, name) representing repositories.
        """

        repositories = set()

        groups = [name for name in os.listdir(self.root) if os.path.isdir(self.to_path(name))]

        for g in groups:
            for name in os.listdir(self.to_path(g)):
                full_path = self.to_path(g, name)
                if os.path.isdir(full_path) and self.__git.exists_local(full_path):
                    repositories.add((g, name))

        return list(sorted(repositories))

    def repo_exists(self, group: str, name: str) -> bool:
        """ Checks if this Resolver can find the path to a repository.

        :param group: Name of the group to check for repo.
        :param name: Name of the repository to check.
        """
        
        try:
            
            all_repos = self.get_all_repos()
            
            if (group, name) in all_repos:
                return True
        except exceptions.MathHubException:
            return False

        return False
