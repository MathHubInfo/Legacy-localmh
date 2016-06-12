from typing import Optional, List, Tuple

from lmh.mathhub.resolvers.local import LocalMathHubResolver
from lmh.mathhub.resolvers.remote import RemoteMathHubResolver

from lmh.utils.caseclass import caseclass

from lmh.mathhub.manager import MathHubManager


@caseclass
class MathHubInstance(object):
    """ Represents a single MathHub instance that has a localResolver and a matching remote resolver. """

    def __init__(self, name: str, local_resolver: LocalMathHubResolver, remote_resolver: RemoteMathHubResolver):
        """ Creates a new MathHubInstance().

        :param name: A string representing the unique name of this MathHubInstance.
        :param local_resolver: A LocalMathHubResolver() instance used to resolve local MathHub respositories.
        :param remote_resolver: A RemoteMathHubResolver() instance used to resolve remote MathHub respositories.
        """

        if not isinstance(local_resolver, LocalMathHubResolver):
            raise TypeError('local_resolver needs to be an instance of local.LocalMathHubResolver()')

        if not isinstance(remote_resolver, RemoteMathHubResolver):
            raise TypeError('remote_resolver needs to be an instance of remote.RemoteMathHubResolver()')
        
        self.__name = name  # type: str
        
        self.__local_resolver = local_resolver  # type: LocalMathHubResolver
        self.__remote_resolver = remote_resolver  # type: RemoteMathHubResolver

    @property
    def name(self) -> str:
        """ Returns the name of this MathHub instance. """

        return self.__name

    @property
    def local(self) -> LocalMathHubResolver:
        """ Returns the LocalMathHubResolver() associated to this MathHubInstance(). """

        return self.__local_resolver

    @property
    def remote(self) -> RemoteMathHubResolver:
        """ Returns the RemoteMathHubResolver() associated to this MathHubInstance(). """

        return self.__remote_resolver
    
    def __repr__(self) -> str:
        """ Returns a string representation of this MathHubInstance. """
        
        return 'MathHubInstance(%r)' % (self.name, )
    
    def can_answer_for(self, name: str) -> bool:
        """ Checks if this instance can answer queries for the given name.
        
        :param name: Name to check against.
        """

        return (
            self.name == name
        ) or (
            self.local.can_answer_for(name)
        ) or (
            self.remote.can_answer_for(name)
        )
    
    def resolve_local(self, *spec: List[str], base_group: Optional[str] = None) -> List[Tuple[str, str]]:
        """ Resolves the specification to a local repository by calling local_resolver.get_repos_matching().

        :param spec: A list of strings or patterns contains *s that will be matched against the full names of
        repositories of the form 'group/name'. If empty and base_group is None, the full list of repositories will be
        returned. If empty and base_group has some value only repositories from that group will be returned.
        :param base_group: Optional. If given, before trying to match repositories globally will try to match 'name'
        inside the group base_group.
        :return: A list of pairs of strings (group, name) representing repositories.
        """
        
        return self.local.get_repos_matching(*spec, base_group=base_group)
    
    def get_local_path(self, group: str, name: str) -> str:
        """ Returns the full path to a local repository. Never throws any exceptions, even if the repository does not
        yet exist locally.

        :param group: The name of the group to find the repository.
        :param name: Name of the repository to find.
        """

        return self.local.get_repo_path(group, name)
    
    def local_exists(self, group: str, name: str) -> bool:
        """ Checks if a local repository exists.
        
        :param group: The name of the group to check the repository in.
        :param name: Name of the repository to check.
        """
        
        return self.local.repo_exists(group, name)
    
    def clear_local_cache(self) -> None:
        """ Clears the cache of repositories of the associated local_resolver. """
        
        return self.local.clear_repo_cache()
    
    def resolve_remote(self, *spec: List[str], base_group: Optional[str] = None) -> List[Tuple[str, str]]:
        """ Resolves the specification to a remote repository by calling remote_resolver.get_repos_matching().
        
        :param spec: A list of strings or patterns contains *s that will be matched against the full names of
        repositories of the form 'group/name'. If empty and base_group is None, the full list of repositories will be
        returned. If empty and base_group has some value only repositories from that group will be returned.
        :param base_group: Optional. If given, before trying to match repositories globally will try to match 'name'
        inside the group base_group.
        :return: A list of pairs of strings (group, name) representing repositories.
        """
        
        return self.remote.get_repos_matching(*spec, base_group = base_group)
    
    def get_remote_path(self, group: str, name: str) -> str:
        """ Returns the git origin to a remote repository.

        :param group: The name of the group to find the repository.
        :param name: Name of the repository to find.
        """

        return self.remote.get_repo_path(group, name)
    
    def remote_exists(self, group: str, name: str) -> bool:
        """ Checks if this Resolver can find the path to a remote repository.
        
        :param group: Name of the group to check for repo.
        :param name: Name of the repository to check.
        """
        
        return self.remote.repo_exists(group, name)
    
    def clear_remote_cache(self) -> None:
        """ Clears the cache of repositories of the associated remote_resolver. """
        
        return self.remote.clear_repo_cache()