from typing import List, Tuple, Optional

from fnmatch import fnmatch

from lmh.utils import exceptions
from deps.PythonCaseClass.case_class import AbstractCaseClass


class MathHubResolver(AbstractCaseClass):
    """ Represents a (local or remote) Resolver that can resolve specifications of repositories. """
    
    def can_answer_for(self, name: str) -> bool:
        """ Performs a partial check if this resolver can answer queries for the given instance name. If this method
        returns true, the MathHubResolver can answer queries, for all other cases the behaviour is unspecified. By
        default returns False, so it should be overridden in a subclass.

        :param name: Name to check
        """
        
        return False

    def _match_name(self, spec: str, group: str, name: str) -> bool:
        """ Protected function used to check if a single name matches a specification. By default uses fnmatch.

        :param spec: Spec to check against.
        :param group: Group in which the name is to be resolved.
        :param name: Name of repository to check against
        """

        return fnmatch(name, spec)

    def _match_full(self, spec: str, group: str, name: str) -> bool:
        """
        Protected function used to check if a full repository name matches a specification. By default uses fnmatch.

        :param spec: Spec to check against.
        :param group: Group of repository to check against.
         :param name: Name of repository to check against.
        """
        return fnmatch('%s/%s' % (group, name), spec)

    def _resolve_group(self, group: str) -> str:
        """ Protected function used to resolve a group name. By default does nothing.

        :param group: Group name to resolve.
        """

        return group
    
    def get_repo_path(self, group: str, name: str) -> str:
        """ Gets the full path to a repository or throws NotImplementedError. May also throw RepositoryNotFound. Should
        be overridden by the subclass.

        :param group: Group of repository to resolve.
        :param name: Name of repository to resolve.
        """
        
        raise NotImplementedError

    def get_all_repos(self) -> List[Tuple[str, str]]:
        """ Gets a (possibly cached) list of repositories or throws NotImplementedError if not available. Should be
        overridden by the subclass.

        :return: A list of pairs of strings (group, name) representing repositories.
        """

        raise NotImplementedError

    def get_all_groups(self) -> List[str]:
        """ Gets a (possibly cached) list of groups available on this MathHubResolver() instance or throws
        NotImplementedError. If not overridden by the subclass finds the groups by checking the output of
        get_all_repos().
        """

        groups = set()

        for (g, n) in self.get_all_repos():
            groups.add(g)

        return list(groups)

    def get_repos_in(self, group: str) -> List[Tuple[str, str]]:
        """ Gets a list of repositories available in a given group on this MathHubResolver() instance or throws
        NotImplementedError. May also throw GroupNotFound() if the given group does not exist. If not overriden by the
        subclass finds the groups by checking the output of get_all_groups() and get_all_repos().

        :param group: Name of the group to find repositories in.
        :return: A list of pairs of strings (group, name) representing repositories.
        """

        group = self._resolve_group(group)

        groups = self.get_all_groups()

        if group not in groups:
            raise GroupNotFound()

        repositories = set()

        for (g, n) in self.get_all_repos():
            if g == group:
                repositories.add((g, n))

        return list(repositories)

    def get_repos_matching(self, *spec: List[str], base_group: Optional[str] = None) -> List[Tuple[str, str]]:
        """ Gets a (possibly cached and ordered) list of repositories matching the given specification. If not
        overridden by the subclass uses the output of get_all_repos() and get_repos_in().

        :param spec: A list of strings or patterns contains *s that will be matched against the full names of
        repositories of the form 'group/name'. If empty and base_group is None, the full list of repositories will be
        returned. If empty and base_group has some value only repositories from that group will be returned.
        :param base_group: Optional. If given, before trying to match repositories globally will try to match 'name'
        inside the group base_group.
        :return: A list of pairs of strings (group, name) representing repositories.
        """
        
        # if we have nothing to resolve, return all the repositories
        # in the appropriate base group
        if len(spec) == 0:
            if base_group is None:
                return self.get_all_repos()
            else:
                return self.get_repos_in(base_group)
        
        # get ready to resolve each of them
        spec_copy = set(spec)
        repositories = set()
        
        # for all the specs, check if a repository with the exact name exists
        # first. 
        for s in spec_copy.copy():
            (g, n) = self.name_to_pair(s)
            if g is not None and self.repo_exists(g, n):
                repositories.add((g, n))
                spec_copy.remove(s)
        
        # next, try to resolve relative to the base group
        if base_group is not None:
            base_group = self._resolve_group(base_group)
            
            for (g, n) in self.get_repos_in(base_group):
                for s in spec_copy:
                    if self._match_name(s, g, n):
                        repositories.add((g, n))
                        spec_copy.remove(s)
                        break
        
        for (g, n) in self.get_all_repos():
            for s in spec_copy:
                if self._match_full(s, g, n):
                    repositories.add((g, n))
                    break
                elif self._match_full('%s/*' % (s), g, n):
                    repositories.add((g, n))
                    break
        
        return list(sorted(repositories))

    def get_repo_matching(self, spec: str, base_group: Optional[str] = None) -> Tuple[str, str]:
        """
        Same as get_repos_matching() but returns only a single repository. Throws RepositoryNotFound() if not repository
        exists. If not overridden by the subclass uses the output of get_repo_matching().

        :param spec: A string or pattern that can contains *s that will be matched against the full names of
        repositories of the form 'group/name'.
        :param base_group: Optional. If given, before trying to match repositories globally will try to match 'name'
        inside the group base_group.
        :return: A single pair (group, name) that represents a repository.
        """

        repositories = self.get_repos_matching(spec, base_group = base_group)

        try:
            return repositories[0]
        except IndexError:
            raise RepositoryNotFound()
    
    def repo_exists(self, group: str, name: str) -> bool:
        """ Checks if this Resolver can find the path to a repository. Should be overridden by subclass for speed
        advantages. By default checks the output of get_all_repos().
        
        :param group: Name of the group to check for repo.
        :param name: Name of the repository to check.
        """
        
        try:
            return (group, name) in self.get_all_repos()
        except exceptions.MathHubException:
            return False
    
    def clear_repo_cache(self) -> None:
        """ Clears the cache of this Resolver. Should be implemented by the subclass. """

        raise NotImplementedError
    
    def name_to_pair(self, s: str) -> Tuple[Optional[str], Optional[str]]:
        """Turns a string representing a repository into a pair (group, name).

        :param s: String of the form group/name representing the name
        :return: a pair (name, group) or (None, None)
        """
        
        comp = s.split('/')
        if len(comp) != 2:
            return None, None
        else:
            return comp[0], comp[1]
        

class RepositoryNotFound(exceptions.MathHubException):
    """ Exception that is thrown when a repository is not found on a MathHubResolver() instance. """

    def __init__(self):
        """ Creates a new RepositoryNotFound() instance. """

        super(RepositoryNotFound, self).__init__('Repository not found on this MathHubResolver() instance. ')


class GroupNotFound(exceptions.MathHubException):
    """ Exception that is thrown when a group is not found on a MathHubResolver() instance. """

    def __init__(self):
        """ Creates a new GroupNotFound() instance. """

        super(GroupNotFound, self).__init__('Group not found on this MathHubResolver() instance. ')
