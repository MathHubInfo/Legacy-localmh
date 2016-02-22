from lmh.mathhub.resolvers import local, remote
from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class MathHubInstance(object):
    """
    Represents a single MathHub instance that has a localResolver and a matching
    remote resolver. 
    """

    def __init__(self, name, local_resolver, remote_resolver):
        """
        Creates a new MathHubInstance().

        Arguments:
            name
                A string representing the unique name of this MathHubInstance
            local_resolver
                A LocalMathHubResolver() instance used to resolve local MathHub
                respositories.
            remote_resolver
                A RemoteMathHubResolver() instance used to resolve remote
                MathHub respositories.
        """

        if not isinstance(local_resolver, local.LocalMathHubResolver):
            raise TypeError('local_resolver needs to be an instance of local.LocalMathHubResolver()')

        if not isinstance(remote_resolver, remote.RemoteMathHubResolver):
            raise TypeError('remote_resolver needs to be an instance of remote.RemoteMathHubResolver()')
        
        self.name = name
        
        self.local_resolver = local_resolver
        self.remote_resolver = remote_resolver
    
    def __repr__(self):
        """
        Returns a string representation of this MathHubInstance. 
        
        Returns: 
            string
        """
        
        return 'MathHubInstance(%r)' % (self.name, )
    
    def can_answer_for(self, name):
        """
        Checks if this instance can answer queries for the given name. 
        
        Arguments:
            name
                Name to check against
        Returns:
            A boolean indicating if this instance matches or not
        """
        
        return (
            self.name == name
        ) or (
            self.local_resolver.can_answer_for(name)
        ) or (
            self.remote_resolver.can_answer_for(name)
        )
    
    def resolve_local(self, *spec, base_group = None):
        """
        Resolves the specification to a local repository by calling
        local_resolver.get_repos_matching(). 
        
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
        
        return self.local_resolver.get_repos_matching(*spec, base_group = base_group)
    
    def get_local_path(self, group, name):
        """
        Returns the full path to a local repository. Never throws any exceptions. 
        
        Arguments:
            group
                The name of the group to find the repository.
            name
                Name of the repository to find.
        Returns:
                A String representing the path to the repository. 
        """
        return self.local_resolver.get_repo_path(group, name)
    
    def local_exists(self, group, name):
        """
        Checks if this Resolver can find the path to a local repository. 
        
        Arguments: 
            group
                Name of the group to check for repo. 
            name
                Name of the repository to check. 
        Returns:
            A boolean indicating if the repository exists or not. 
        """
        
        return self.local_resolver.repo_exists(group, name)
    
    def clear_local_cache(self):
        """
        Clears the cache of local repositories. 
        """
        
        return self.local_resolver.clear_repo_cache()
    
    def resolve_remote(self, *spec, base_group = None):
        """
        Resolves the specification to a remote repository by calling
        remote_resolver.get_repos_matching(). 
        
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
        
        return self.remote_resolver.get_repos_matching(*spec, base_group = base_group)
    
    def get_remote_path(self, group, name):
        """
        Returns the git origin to a remote repository. 
        
        Arguments:
            group
                The name of the group to find the repository.
            name
                Name of the repository to find.
        Returns:
                A String representing the path to the repository. 
        """
        return self.remote_resolver.get_repo_path(group, name)
    
    def remote_exists(self, group, name):
        """
        Checks if this Resolver can find the path to a remote repository. 
        
        Arguments: 
            group
                Name of the group to check for repo. 
            name
                Name of the repository to check. 
        Returns:
            A boolean indicating if the repository exists or not. 
        """
        
        return self.remote_resolver.repo_exists(group, name)
    
    def clear_remote_cache(self):
        """
        Clears the cache of remote repositories. 
        """
        
        return self.remote_resolver.clear_repo_cache()