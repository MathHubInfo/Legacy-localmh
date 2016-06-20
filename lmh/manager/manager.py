from typing import Optional, Dict, List, Any, Union, Tuple

from lmh.mathhub.resolvers import resolver
from lmh.utils import exceptions
from lmh.archives.archive import Archive
from lmh.archives.local import LocalArchive
from lmh.archives.remote import RemoteArchive

from lmh.actions.action import Action

from lmh.logger.logger import Logger
from lmh.mathhub.manager import MathHubManager
from lmh.systems.manager import SystemManager
from lmh.config.config import LMHConfig


class LMHManager(object):
    """ The main object that is instantiated by lmh. """
    
    def __init__(self, logger: Optional[Logger] = None,
                 config: Optional[LMHConfig] = None,
                 mathhub: Optional[MathHubManager] = None,
                 systems: Optional[SystemManager] = None):
        """ Creates a new LMHManager() instance.

        :param logger: Optional. Logger Instance to be used by this
        LMHManager(). If omitted should be set before any actions are
        registered by setting the logger property.
        :param config: Optional. Configuration Instance to be used by this
        LMHManager(). If omitted should be set before any actions are
        registered by setting the config property.
        :param mathhub: Optional. MathHubManager used by this LMHManager(). If
        omitted should be set before any actions are registered by setting the
        mathhub property.
        :param systems: Optional. SystemManager used by this LMHManager(). If
        omitted should be set before any actions are registered by setting the
        systems property.
        """
        
        self.__logger = logger  # type: Optional[Logger]
        self.__config = config  # type: Optional[LMHConfig]
        self.__mathhub = mathhub  # type: Optional[MathHubManager]
        self.__systems = systems  # type: Optional[SystemManager]

        self.__actions = []  # type: List[Action]
        self.__archives = {}  # type: Dict[str, Archive]
    
    #
    # Properties
    #
    
    @property
    def logger(self) -> Logger:
        """ Gets the Loggger instance belonging to this LMHManager() or raises
        ManagerWithoutLogger().
        """
        
        if self.__logger == None:
            raise ManagerWithoutLogger()
        
        return self.__logger
    
    @logger.setter
    def logger(self, logger : Logger) -> None:
        """ Sets the Logger instance to be used by this LMHManager().
        
        :param logger: Logger instance to be set.
        """
        
        self.__logger = logger
    
    @property
    def config(self) -> LMHConfig:
        """ Gets the LMHConfig instance belonging to this LMHManager() or
        raises ManagerWithoutConfig().
        """
        
        if self.__config == None:
            raise ManagerWithoutConfig()
        
        return self.__config
    
    @config.setter
    def config(self, config: LMHConfig) -> None:
        """ Sets the LMHConfig instance to be used by this LMHManager().

        :param logger: LMHConfig instance to be set.
        """
        
        self.__config = config
    
    @property
    def mathhub(self) -> MathHubManager:
        """ Gets the MathHubManager instance belonging to this LMHManager() or
        raises ManagerWithoutMathhub().
        """
        
        if self.__mathhub == None:
            raise ManagerWithoutMathhub()
        
        return self.__mathhub
    
    @mathhub.setter
    def mathhub(self, mathhub : MathHubManager) -> None:
        """ Sets the MathHubManager instance to be used by this LMHManager().
        
        :param mathhub: MathHubManager instance to be set.
        """
        
        self.__mathhub = mathhub
    
    @property
    def systems(self) -> SystemManager:
        """ Gets the SystemManager instance belonging to this LMHManager() or
        raises ManagerWithoutSystems().
        """
        
        if self.__systems == None:
            raise ManagerWithoutSystems()
        
        return self.__systems
    
    @systems.setter
    def systems(self, systems: SystemManager) -> None:
        """ Sets the SystemManager instance to be used by this LMHManager().
        
        :param systems: SystemManager instance to be set.
        """
        
        self.__systems = systems
    
    #
    # Action Functionality
    #
    
    def add(self, act: Action) -> None:
        """ Adds an Action to this LMHManager() instance.
        
        :param act: Action to add to this instance
        """
        
        if not isinstance(act, Action):
            raise TypeError("act must be an instance of Action()")
        
        if act.name in self:
            raise ValueError(
                'LMHManager() already has an action named %r' % act.name)
        
        act.register(self)
        self.__actions.append(act)
    
    def __iadd__(self, act: Action):
        """ Same as self.add(act).

        :rtype: LMHManager
        """

        self.add(act)
        return self
    
    def keys(self) -> List[str]:
        """ Returns the names of all actions in this LMHManager. """
        
        return list(map(lambda a:a.name, self.__actions))
    
    def has_action(self, name: str) -> bool:
        """ Checks if this Manager contains an action with the given name.
        
        :param name: Name of action to search for.
        """
        
        return name in self.keys()
    
    def __contains__(self, name: str) -> bool:
        """ Same as self.has_action(name).  """
        
        return self.has_action(name)
    
    def get(self, name: str) -> Action:
        """ Gets the action with the given name or raises KeyError if it does
        not exist.
        
        :param name: Name of action to search for.
        """
        
        for k in self.__actions:
            if k.name == name:
                return k
        
        raise KeyError

    def __getitem__(self, name: str) -> Action:
        """ Same as self.get(name). """

        return self.get(name)
    
    def __call__(self, name: str, *args: List[Any], **kwargs : Dict[str, Any]) \
            -> Any:
        """ Gets an action and calls it with the given arguments.

        :param name: Name of action to search for.
        :param args: Arbitrary positional arguments to pass on to the action.
        :param kwargs: Arbitrary keyword arguments to pass on to the action.
        :return: The result of the Action.
        """
        
        return (self[name])(*args, **kwargs)
    
    #
    # Archive Functionality
    #
    def get_archive(self, instance: str, group: str, name: str) -> Archive:
        """ Retrieves an Archive() instance contained in this LMHManager.
        
        :param instance: Name of the MathHubInstance to retrieve the Archive
        from.
        :param group: Name of the group to retrieve the instance from.
        :param name: Name of the archive to retrieve.
        """
        
        # if the archive is cached return the cached one
        if (instance, group, name) in self.__archives.keys():
            return self.__archives[(instance, group, name)]
        
        # put it into the cache
        self.__archives[(instance, group, name)] = \
            Archive(self.mathhub[instance], group, name)
        
        # and return it
        return self.__archives[(instance, group, name)]
    
    def resolve_local_archives(self, *spec: List[Union[str, Tuple[str, str],
                                                       Archive]],
                               base_group: Optional[str] = None,
                               instance: Optional[str] = None)\
            -> List[LocalArchive]:
        """ Retrieves all LocalArchive() instances matching the given
        specification.
        
        :param spec: A list of strings, pairs, LMHArchive or patterns
        containing *s that will be matched against the full names of
        repositories of the form 'group/name'. If empty and base_group is None,
        the full list of repositories will be returned. If empty and base_group
        has some value only repositories from that group will be returned.
        :param base_group: Optional. If given, before trying to match
        repositories globally will try to match 'name' inside the
        group base_group.
        :param instance: Optional. If set returns only repositories from the
        instance matching the given name.
        """
        
        the_spec = []
        the_archives = []
        has_work = (len(spec) == 0)
        
        for s in spec:
            if isinstance(s, Archive):
                the_archives.append(s.to_local_archive())
            elif isinstance(s, tuple) and len(s) == 2:
                the_spec.append('%s/%s' % s)
                has_work = True
            else:
                the_spec.append(s)
                has_work = True
        
        if has_work:
            the_archives += [
                self.get_archive(i, g, n).to_local_archive()
                for (i, g, n) in self.mathhub.resolve_local(*the_spec,
                                                            base_group =
                                                            base_group,
                                                            instance =
                                                            instance)
            ]
        
        the_archives.sort(key=str)
        return the_archives
    
    def resolve_local_archive(self, spec: Union[str, Tuple[str, str], Archive],
                              base_group: Optional[str] = None,
                              instance: Optional[str] = None) -> LocalArchive:
        """ Retrieves a single LocalArchive() instance that matches a
        specification or raises RepositoryNotFound().

        :param spec: A string, pair, LMHArchive or pattern containing *s that
        will be matched against the full names of repositories of the form
        'group/name'.
        :param base_group: Optional. If given, before trying to match
        repositories globally will try to match 'name' inside the
        group base_group.
        :param instance: Optional. If set returns only repositories from the
        instance matching the given name.
        """
        
        repos = self.resolve_local_archives(spec, base_group = base_group,
                                            instance = instance)
        
        if len(repos) >= 1:
            return repos[0]
        else:
            raise resolver.RepositoryNotFound()
    
    def resolve_remote_archives(self, *spec: List[Union[str, Tuple[str, str],
                                                       Archive]],
                               base_group: Optional[str] = None,
                               instance: Optional[str] = None)\
            -> List[RemoteArchive]:
        """
        Retrieves all RemoteArchive() instances matching the given
        specification.
        
        :param spec: A list of strings, pairs, LMHArchive or patterns
        containing *s that will be matched against the full names of
        repositories of the form 'group/name'. If empty and base_group is None,
        the full list of repositories will be returned. If empty and base_group
        has some value only repositories from that group will be returned.
        :param base_group: Optional. If given, before trying to match
        repositories globally will try to match 'name' inside the
        group base_group.
        :param instance: Optional. If set returns only repositories from the
        instance matching the given name.
        """
        
        the_spec = []
        the_archives = []
        has_work = (len(spec) == 0)
        
        for s in spec:
            if isinstance(s, Archive):
                the_archives.append(s.to_remote_archive())
            elif isinstance(s, tuple) and len(s) == 2:
                the_spec.append('%s/%s' % s)
                has_work = True
            else:
                the_spec.append(s)
                has_work = True
        
        if has_work:
            the_archives += [
                self.get_archive(i, g, n).to_remote_archive()
                for (i, g, n) in self.mathhub.resolve_remote(*the_spec,
                                                             base_group =
                                                             base_group,
                                                             instance =
                                                             instance)
            ]
        
        the_archives.sort(key=str)
        return the_archives
    
    def resolve_remote_archive(self, spec: Union[str, Tuple[str, str], Archive],
                              base_group: Optional[str] = None,
                              instance: Optional[str] = None) -> RemoteArchive:
        """ Retrieves a single RemoteArchive() instance that matches a
        specification or raises RepositoryNotFound().

        :param spec: A string, pair, LMHArchive or pattern containing *s that
        will be matched against the full names of repositories of the form
        'group/name'.
        :param base_group: Optional. If given, before trying to match
        repositories globally will try to match 'name' inside the
        group base_group.
        :param instance: Optional. If set returns only repositories from the
        instance matching the given name.
        """
        
        repos = self.resolve_remote_archives(spec, base_group = base_group,
                                             instance = instance)
        
        if len(repos) >= 1:
            return repos[0]
        else:
            raise resolver.RepositoryNotFound()


class ManagerWithoutLogger(exceptions.LMHException):
    """ Exception that is thrown when no Logger() is bound to an LMHManager()
    instance.
    """
    
    def __init__(self):
        """ Creates a new ManagerWithoutLogger() instance. """
        
        super(ManagerWithoutLogger, self).__init__('No Logger() is bound to ' +
                                                   'this LMHManager() instance')


class ManagerWithoutConfig(exceptions.LMHException):
    """ Exception that is thrown when no LMHConfig() is bound to an LMHManager()
     instance.
    """
    
    def __init__(self):
        """ Creates a new ManagerWithoutConfig() instance. """
        
        super(ManagerWithoutConfig, self).__init__('No LMHConfig() is bound ' +
                                                   'to this LMHManager() ' +
                                                   'instance')


class ManagerWithoutMathhub(exceptions.LMHException):
    """
    Exception that is thrown when no MathHubManager() is bound to an
    LMHManager() instance.
    """
    
    def __init__(self):
        """ Creates a new ManagerWithoutMathhub() instance. """
        
        super(ManagerWithoutMathhub, self).__init__('No MathHubManager() is ' +
                                                    'bound to this ' +
                                                    'LMHManager() instance')

class ManagerWithoutSystems(exceptions.LMHException):
    """ Exception that is thrown when no ManagerWithoutSystems() is bound to
    an LMHManager() instance.
    """

    def __init__(self):
        """ Creates a new ManagerWithoutSystems() instance. """

        super(ManagerWithoutSystems, self).__init__(
            'No SystemManager() is bound to this LMHManager() instance')

__all__ = ["LMHManager", "ManagerWithoutLogger", "ManagerWithoutConfig",
           "ManagerWithoutMathhub", "ManagerWithoutSystems"]
