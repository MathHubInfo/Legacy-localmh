from typing import Dict, Tuple, List, Optional
from lmh.utils import exceptions


class MathHubManager(object):
    """ Represents a Manager that can contain multiple MathHub Instances. """
    
    def __init__(self):
        """ Creates a new MathHubManager() instance. """
        
        self.__hubs = {}  # type: Dict[str,MathHubInstance]
    
    def add(self, mh_instance) -> None:
        """ Adds a new MathHubInstance() to this MathHubManager() or throws
        InstanceAlreadyRegistered() if it is already
        registered.

        :param mh_instance: MathHubInstance to add.
        :type mh_instance: MathHubInstance
        """
        
        if not isinstance(mh_instance, MathHubInstance):
            raise TypeError("mh_instance must be a MathHubInstance()")
        
        if mh_instance.name in self.__hubs.keys():
            raise InstanceAlreadyRegistered()
        
        self.__hubs[mh_instance.name] = mh_instance
    
    def __iadd__(self, mh_instance):
        """ Same as self.add(mh_instance).

        :type mh_instance: MathHubInstance
        :rtype: MathHubManager
        """
        
        self.add(mh_instance)
        return self
    
    def get(self, name: str):
        """ Returns a MathHubInstance() that can resolve queries for the given
        name or throws InstanceNotFound().

        :param name: Name of the instance of path the instance should be able
        to resolve queries for.
        :rtype : MathHubInstance
        """
        
        for (n, instance) in self.__hubs.items():
            if instance.can_answer_for(name):
                return instance
        
        raise InstanceNotFound()
    
    def __getitem__(self, name: str):
        """ Same as self.get(name).
        :rtype : MathHubInstance
        """
        return self.get(name)
    
    def resolve_local(self, *spec: List[str], base_group: Optional[str] = None,
                      instance: Optional[str] = None)\
            -> List[Tuple[str, str, str]]:
        """ Resolves the specification to a local repository within one or all
        MathHubInstances() available in this MathHubManager() and returns
        triples of (instance, group, name) strings.

        :param spec: A list of strings or patterns contains *s that will be
        matched against the full names of repositories of the form 'group/name'.
        If empty and base_group is None, the full list of repositories will be
        returned. If empty and base_group has some value only repositories from
        that group will be returned.
        :param base_group: Optional. If given, before trying to match
        repositories globally will try to match 'name' inside the group
        base_group.
        :param instance: Optional. If set returns only repositories from the
        instance matching the given name.
        """
        
        if instance is not None:
            inst = self[instance]

            return [
                (instance, g, n) for (g, n) in inst.resolve_local(*spec,
                                                                  base_group=
                                                                  base_group)
            ]
        
        repos = set()
        
        for instance in self.__hubs.keys():
            repos.update(self.resolve_local(*spec, base_group = base_group,
                                            instance = instance))
        
        return list(sorted(repos))
    
    def get_local_path(self, instance: str, group: str, name: str) -> str:
        """ Gets the (full) path to a local repository given by a triple.
        May throw InstanceNotFound or RepositoryNotFound.

        :param instance: Name of instance to get full path to.
        :param group: Name of group to get full path to.
        :param name: Name of repository to find.
        """
        
        return self[instance].get_repo_path(group, name)

    def resolve_remote(self, *spec: List[str], base_group: Optional[str] = None,
                       instance: Optional[str] = None)\
            -> List[Tuple[str, str, str]]:
        """ Resolves the specification to a remote repository within one or all
        MathHubInstances() available in this MathHubManager() and returns
        triples of (instance, group, name) strings.

        :param spec: A list of strings or patterns contains *s that will be
        matched against the full names of repositories of the form 'group/name'.
        If empty and base_group is None, the full list of repositories will be
        returned. If empty and base_group has some value only repositories from
        that group will be returned.
        :param base_group: Optional. If given, before trying to match
        repositories globally will try to match 'name' inside the group
        base_group.
        :param instance: Optional. If set returns only repositories from the
        instance matching the given name.
        """
        
        if instance is not None:
            inst = self[instance]

            return [
                (instance, g, n) for (g, n) in inst.resolve_remote(*spec,
                                                                   base_group =
                                                                   base_group)
            ]
        
        repos = set()
        
        for instance in self.__hubs.keys():
            repos.update(self.resolve_remote(*spec, base_group = base_group,
                                             instance = instance))
        
        return list(sorted(repos))
    
    def get_remote_path(self, instance: str, group: str, name: str) -> str:
        """ Gets the (full) path to a remote repository given by a triple. May
        throw InstanceNotFound or RepositoryNotFound.

        :param instance: Name of instance to get full path to.
        :param group: Name of group to get full path to.
        :param name: Name of repository to find.
        """
        
        return self[instance].get_repo_path(group, name)


class InstanceAlreadyRegistered(exceptions.MathHubException):
    """ Exception that is thrown when a given instance is already registered in
    this MathHubManager(). """

    def __init__(self):
        """ Creates a new InstanceAlreadyRegistered() instance. """

        super(InstanceAlreadyRegistered, self).__init__('Instance already ' +
                                                        'exists in this ' +
                                                        'MathHubManager() ' +
                                                        'instance. ')


class InstanceNotFound(exceptions.MathHubException):
    """ Exception that is thrown when the given instance does not exist in this
    MathHubManager(). """

    def __init__(self):
        """ Creates a new InstanceNotFound() instance. """

        super(InstanceNotFound, self).__init__('Instance not found on this ' +
                                               'MathHubManager() instance. ')

# avoiding the circular import
from lmh.mathhub.instance import MathHubInstance

__all__ = ["MathHubManager", "InstanceAlreadyRegistered", "InstanceNotFound"]
