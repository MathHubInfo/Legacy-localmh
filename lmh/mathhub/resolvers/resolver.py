from fnmatch import fnmatch

from lmh.utils import exceptions
from lmh.utils.caseclass import caseclass

@caseclass
class MathHubResolver(object):
    """
    Represents a (local or remote) Resolver that can resolve specifications of
    repositories.
    """
    
    def can_answer_for(self, name):
        """
        If this function returns True that means this resolver can answer queries
        for the given instance name. For all other cases the behaviour is 
        unspecefied. By default returns False, so it should be overriden in a 
        subclass. 
        
        Arguments:
            name
                Name to check against
        Returns:
            A boolean indicating if this instance matches or not
        """
        
        return False

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
        Returns:
            A boolean indicating if the spec matches.
        """

        return fnmatch(name, spec)

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
        Returns:
            A boolean indicating if the spec matches.
        """
        return fnmatch('%s/%s' % (group, name), spec)

    def _resolve_group(self, group):
        """
        Private function used to resolve a group name. By default does nothing.

        Arguments:
            group
        Returns:
            A string representing the resolved group name.
        """
        return group
    
    def get_repo_path(self, group, name):
        """
        Gets the full path to a repository or throws NotImplementedError. May 
        also throw RepositoryNotFound. Should be overriden by the subclass.
        
        Arguments:
            group
                Group of repository to resolve
            name
                Name of repository to resolve

        Returns:
            A string representing the path
        """
        
        raise NotImplementedError

    def get_all_repos(self):
        """
        Gets a (cached) list of repositories or throws NotImplementedError
        if not available. Should be overriden by the subclass.

        Returns:
            A list of pairs of strings (group, name) representing repositories.
        """

        raise NotImplementedError

    def get_all_groups(self):
        """
        Gets a list of groups available on this MathHubResolver() instance or
        throws NotImplementedError. If not overriden by the subclass finds the
        groups by checking the output of get_all_repos().

        Returns:
            A list of strings representing the names of all available groups.
        """

        groups = set()

        for (g, n) in self.get_all_repos():
            groups.add(g)

        return list(groups)

    def get_repos_in(self, group):
        """
        Gets a list of repositories available in a given group on this
        MathHubResolver() instance or throws NotImplementedError. May also throw
        GroupNotFound() if the given group does not exist.
        If not overriden by the subclass finds the groups by
        checking the output of get_all_groups() and get_all_repos().

        Arguments:
            group
                Name of the group to find repositories in
        Returns:
            A list of pairs of strings (group, name) representing repositories.
        """

        group = self._resolve_group(group)

        groups = self.get_all_groups()

        if not group in groups:
            raise GroupNotFound()

        repositories = set()

        for (g, n) in self.get_all_repos():
            if g == group:
                repositories.add((g, n))

        return list(repositories)

    def get_repos_matching(self, *spec, base_group = None):
        """
        Gets a (cached and ordered) list of repositories matching the given
        specification. If not overriden by the subclass uses the output of
        get_all_repos() and get_repos_in().

        Arguments:
            *spec
                A list of strings or patterns contains *s that will be matched
                against the full names of repositories of the form 'group/name'.
                If empty and base_group is None, the full list of repositories 
                will be returned. If empty and base_group has some value only
                repositories from that group will be returned. 
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group.
        Returns:
            A list of pairs of strings (group, name) representing repositories.
        """
        
        # if we have nothing to resolve, return all the repositories
        # in the appropriate base group
        if len(spec) == 0:
            if base_group == None:
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
            if g != None and self.repo_exists(g, n):
                repositories.add((g, n))
                spec_copy.remove(s)
        
        # next, try to resolve relative to the base group
        if base_group != None:
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

    def get_repo_matching(self, spec, base_group = None):
        """
        Same as get_repos_matching() but returns only a single repository. If
        not overriden by the subclass uses the output of get_repo_matching().

        Arguments:
            spec
                A string or pattern that can contains *s that will be matched
                against the full names of repositories of the form 'group/name'
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group.
        Returns:
            A single pair (group, name) that represents a repository
        """

        repositories = self.get_repos_matching(spec, base_group = base_group)

        if len(repositories) == 0:
            raise RepositoryNotFound()
        else:
            return repositories[0]
    
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
            return ((group, name) in self.get_all_repos())
        except exceptions.MathHubException:
            return False
    
    def clear_repo_cache(self):
        """
        Clears the cache of this Resolver. Should be implemented by the subclass. 
        """
        raise NotImplementedError
    
    def name_to_pair(self, name):
        """
        Turns the name of a repository into a pair (group, name). 
        
        Areguments:
            name
                Name to split
        Returns:
            a pair (name, group) or (None, None)
        """
        
        comp = name.split('/')
        if len(comp) != 2:
            return (None, None)
        else:
            return (comp[0], comp[1])
        

class RepositoryNotFound(exceptions.MathHubException):
    """
    Exception that is thrown when a repository is not found on a
    MathHubResolver() instance.
    """
    def __init__(self):
        super(RepositoryNotFound, self).__init__('Repository not found on this MathHubResolver() instance. ')

class GroupNotFound(exceptions.MathHubException):
    """
    Exception that is thrown when a group is not found on a MathHubResolver()
    instance.
    """
    def __init__(self):
        super(GroupNotFound, self).__init__('Group not found on this MathHubResolver() instance. ')
