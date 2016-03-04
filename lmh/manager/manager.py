from lmh.mathhub.resolvers import resolver
from lmh.utils import exceptions
from lmh.archives import archive
import os

class LMHManager(object):
    """
    An LMHManager is the main object instatiated by lmh. 
    """
    
    def __init__(self, logger = None, config = None, mathhub = None, systems = None):
        """
        Creates a new LMHManager instance. 
        
        Arguments: 
            logger
                Optional. Logger Instance to be used by this LMHManager(). If 
                omitted should be set before any actions are registered by 
                setting the logger property. 
            config
                Optional. Configuration Instance to be used by this 
                LMHManager(). If omitted should be set before any actions are 
                registered by setting the config property. 
            mathhub
                Optional. MathHubManager used by this LMHManager(). If omitted 
                should be set before any actions are registered by setting the 
                mathhub property. 
            systems
                Optional. SystemManager used by this LMHManager(). If omitted
                should be set before any actions are registered by setting the
                systems property. 
        """
        
        self.__logger = logger
        self.__config = config
        self.__mathhub = mathhub
        self.__systems = systems
        
        self.__actions = []
        self.__archives = {}
    
    #
    # Properties
    #
    
    @property
    def logger(self):
        """
        Gets the Loggger instance belonging to this LMHManager() or throws 
        ManagerWithoutLogger(). 
        
        Returns:
            A LMHManager() instance
        """
        
        if self.__logger == None:
            raise ManagerWithoutLogger()
        
        return self.__logger
    
    @logger.setter
    def logger(self, logger):
        """
        Sets the Logger instance to be used by this LMHManager(). 
        
        Arguments:
            logger
                Logger instance to be set
        """
        
        self.__logger = logger
    
    @property
    def config(self):
        """
        Gets the LMHConfig instance belonging to this LMHManager() or throws 
        ManagerWithoutConfig(). 
        
        Returns:
            An LMHConfig() instance
        """
        
        if self.__config == None:
            raise ManagerWithoutConfig()
        
        return self.__config
    
    @config.setter
    def config(self, config):
        """
        Sets the LMHConfig instance to be used by this LMHManager(). 
        
        Arguments:
            config
                LMHConfig instance to be set
        """
        
        self.__config = config
    
    @property
    def mathhub(self):
        """
        Gets the MathHubManager instance belonging to this LMHManager() or throws 
        ManagerWithoutMathhub(). 
        
        Returns:
            An MathHubManager() instance
        """
        
        if self.__mathhub == None:
            raise ManagerWithoutMathhub()
        
        return self.__mathhub
    
    @mathhub.setter
    def mathhub(self, mathhub):
        """
        Sets the MathHubManager instance to be used by this LMHManager(). 
        
        Arguments:
            mathhub
                MathHubManager instance to be set
        """
        
        self.__mathhub = mathhub
    
    @property
    def systems(self):
        """
        Gets the SystemManager instance belonging to this LMHManager() or throws 
        ManagerWithoutSystems(). 
        
        Returns:
            An SystemManager() instance
        """
        
        if self.__systems == None:
            raise ManagerWithoutSystems()
        
        return self.__systems
    
    @systems.setter
    def systems(self, systems):
        """
        Sets the SystemManager instance to be used by this LMHManager(). 
        
        Arguments:
            systems
                SystemManager instance to be set
        """
        
        self.__systems = systems
    
    #
    # Action Functionality
    #
    
    def add(self, act):
        """
        Adds an Action to this LMHManager() instance. 
        
        Arguments: 
            act
                Action to add to this instance
        """
        
        from lmh.actions import action
        
        if not isinstance(act, action.Action):
            raise TypeError("act must be an instance of Action()")
        
        if act.name in self:
            raise ValueError('LMHManager() already has an action named %r' % act.name)
        
        act.register(self)
        self.__actions.append(act)
    
    def __iadd__(self, act):
        """
        Same as self.add(act)
        """
        self.add(act)
        return self
    
    def keys(self):
        """
        Returns the names of all actions in this LMHManager. 
        
        Returns: 
            A list of strings representing the names of the actions in this LMHManager
        """
        
        return list(map(lambda a:a.name, self.__actions))
    
    def has_action(self, name):
        """
        Checks if this Manager contains an action with the given name. 
        
        Arguments:
            name
                Name of action to search for
        Returns:
            A boolean indicating if the action is contained or not
        """
        
        return name in self.keys()
    
    def __contains__(self, name):
        """
        Same as self.has_action(name)
        """
        
        return self.has_action(name)
    
    def get(self, name):
        """
        Gets the action with the given name or throws KeyError if it does not
        exist. 
        
        Arguments:
            name
                Name of action to search for
        Returns:
            A Action() instance
        """
        
        for k in self.__actions:
            if k.name == name:
                return k
        
        raise KeyError
    
    def __call__(self, name, *args, **kwargs):
        """
        Gets an action and calls it with the given arguments. 
        
        Arguments:
            name
                Name of action to search for
            *args, **kwargs
                Arbirtrary arguments to pass on to the action. 
        Returns:
            An Arbritrary object representing the result of the action
        """
        
        return (self[name])(*args, **kwargs)
    
    def __getitem__(self, name):
        """
        Same as self.get(name)
        """
        return self.get(name)
    
    #
    # Archive Functionality
    #
    def get_archive(self, instance, group, name):
        """
        Retrieves an Archive() instance related to this LMHManager. 
        
        Arguments: 
            instance
                Name of the MathHubInstance to retrieve the Archive from
            group
                Name of the group to retrieve the instance form
            name
                Name of the archive to retrieve
        Returns: 
            An Archive() instance
        """
        
        # if the archive is cached return the cached one
        if (instance, group, name) in self.__archives.keys():
            return self.__archives[(instance, group, name)]
        
        # put it into the cache
        from lmh.archives import archive
        self.__archives[(instance, group, name)] = archive.LMHArchive(self.mathhub[instance], group, name)
        
        # and return it
        return self.__archives[(instance, group, name)]
    
    def resolve_local_archives(self, *spec, base_group = None, instance = None):
        """
        Retrieves all LocalArchive() instances matching the given specification. 
        
        Arguments:
            *spec
                A list of strings, pairs, LMHArchive or patterns containing *s 
                that will be matched against the full names of repositories of 
                the form 'group/name'.
                If empty and base_group is None, the full list of repositories 
                will be returned. If empty and base_group has some value only
                repositories from that group will be returned. 
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group. 
            instance
                Optional. If set returns only repositories from the 
                instance matching the given name. 
        Returns: 
            A list of LocalArchive() instances
        """
        
        the_spec = []
        the_archives = []
        has_work = (len(spec) == 0)
        
        for s in spec:
            if isinstance(s, archive.LMHArchive):
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
                for (i, g, n) in self.mathhub.resolve_local(*the_spec, base_group = base_group, instance = instance)
            ]
        
        the_archives.sort(key=str)
        return the_archives
    
    def resolve_local_archive(self, spec, base_group = None, instance = None):
        """
        
        Retrieves a single LocalArchive() instance that matches a specification or 
        throws RepositoryNotFound()
        Arguments:
            spec
                A string, pair, LMHArchive or pattern containing *s 
                that will be matched against the full names of repositories of 
                the form 'group/name'. 
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group. 
            instance
                Optional. If set returns only repositories from the 
                instance matching the given name. 
        Returns: 
            A LocalArchive() instance
        """
        
        repos = self.resolve_local_archives(spec, base_group = base_group, instance = instance)
        
        if len(repos) >= 1:
            return repos[0]
        else:
            raise resolver.RepositoryNotFound()
    
    def resolve_remote_archives(self, *spec, base_group = None, instance = None):
        """
        Retrieves all RemoteArchive() instances matching the given specification. 
        
        Arguments:
            *spec
                A list of strings, pairs, LMHArchive or patterns containing *s 
                that will be matched against the full names of repositories of 
                the form 'group/name'.
                If empty and base_group is None, the full list of repositories 
                will be returned. If empty and base_group has some value only
                repositories from that group will be returned. 
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group. 
            instance
                Optional. If set returns only repositories from the 
                instance matching the given name. 
        Returns: 
            A list of RemoteArchive() instances
        """
        
        the_spec = []
        the_archives = []
        has_work = (len(spec) == 0)
        
        for s in spec:
            if isinstance(s, archive.LMHArchive):
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
                for (i, g, n) in self.mathhub.resolve_remote(*the_spec, base_group = base_group, instance = instance)
            ]
        
        the_archives.sort(key=str)
        return the_archives
    
    def resolve_remote_archive(self, spec, base_group = None, instance = None):
        """
        
        Retrieves a single RemoteArchive() instance that matches a specification or 
        throws RepositoryNotFound()
        Arguments:
            spec
                A string, pair, LMHArchive or pattern containing *s 
                that will be matched against the full names of repositories of 
                the form 'group/name'. 
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group. 
            instance
                Optional. If set returns only repositories from the 
                instance matching the given name. 
        Returns: 
            A RemoteArchive() instance
        """
        
        repos = self.resolve_remote_archives(spec, base_group = base_group, instance = instance)
        
        if len(repos) >= 1:
            return repos[0]
        else:
            raise resolver.RepositoryNotFound()

class ManagerWithoutLogger(exceptions.LMHException):
    """
    Exception that is thrown when no Logger() is bound to an LMHManager() instance
    """
    
    def __init__(self):
        """
        Creates a new ManagerWithoutLogger() instance
        """
        
        super(ManagerWithoutLogger, self).__init__('No Logger() is bound to this LMHManager() instance')

class ManagerWithoutConfig(exceptions.LMHException):
    """
    Exception that is thrown when no LMHConfig() is bound to an LMHManager() instance
    """
    
    def __init__(self):
        """
        Creates a new ManagerWithoutConfig() instance
        """
        
        super(ManagerWithoutConfig, self).__init__('No LMHConfig() is bound to this LMHManager() instance')

class ManagerWithoutMathhub(exceptions.LMHException):
    """
    Exception that is thrown when no MathHubManager() is bound to an LMHManager() instance
    """
    
    def __init__(self):
        """
        Creates a new ManagerWithoutMathhub() instance
        """
        
        super(ManagerWithoutMathhub, self).__init__('No MathHubManager() is bound to this LMHManager() instance')