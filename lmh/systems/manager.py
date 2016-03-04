from lmh.utils import exceptions
class SystemManager(object):
    """
    A Manager that manages all systems known to lmh
    """
    
    def __init__(self, manager = None):
        """
        Creates a new SystemManager instance. 
        
        Arguments: 
            manager
                Optional. LMHManager() Instance to be used by this SystemManager(). If 
                omitted should be set before any actions are registered by 
                setting the manager property. 
        """
        
        self.__manager = manager
        self.__systems = []
    #
    # Properties
    #
    
    @property
    def manager(self):
        """
        Gets the LMHManager() instance belonging to this SystemManager()
        
        Returns:
            A LMHManager() instance
        """
        
        if self.__manager == None:
            raise SystemWithoutManager()
        
        return self.__manager
    
    @manager.setter
    def manager(self, manager):
        """
        Sets the LMHManager instance to be used by this SystemManager(). 
        
        Arguments:
            manager
                Manager instance to be set
        """
        
        self.__manager = manager
    
    #
    # System Functionality
    #
    
    def add(self, system):
        """
        Adds a System to this SystemManager() instance. 
        
        Arguments: 
            system
                System to add to this instance
        """
        
        from lmh.systems import system
        
        if not isinstance(act, system.System):
            raise TypeError("system must be an instance of System()")
        
        if system.name in self:
            raise ValueError('SystemManager() already has a system named %r' % system.name)
        
        system.register(self)
        self.__systems.append(system)
    
    def __iadd__(self, system):
        """
        Same as self.add(system)
        """
        self.add(system)
        return self
    
    def keys(self):
        """
        Returns the names of all systems in this SystemManager. 
        
        Returns: 
            A list of strings representing the names of the actions in this SystemManager
        """
        
        return list(map(lambda s:s.name, self.__systems))
    
    def has_system(self, name):
        """
        Checks if this SystemManager contains a system with the given name. 
        
        Arguments:
            name
                Name of system to search for
        Returns:
            A boolean indicating if the system is contained or not
        """
        
        return name in self.keys()
    
    def __contains__(self, name):
        """
        Same as self.has_system(name)
        """
        
        return self.has_system(name)
    
    def get(self, name):
        """
        Gets the system with the given name or throws KeyError if it does not
        exist. 
        
        Arguments:
            name
                Name of system to search for
        Returns:
            A Action() instance
        """
        
        for s in self.__systems:
            if s.name == name:
                return s
        
        raise KeyError
    
    def __getitem__(self, name):
        """
        Same as self.get(name)
        """
        return self.get(name)

class SystemWithoutManager(exceptions.LMHException):
    """
    Exception that is thrown when no LMHManager() is bound to an SystemManager() instance
    """
    
    def __init__(self):
        """
        Creates a new SystemWithoutManager() instance
        """
        
        super(SystemWithoutManager, self).__init__('No LMHManager() is bound to this SystemManager() instance')