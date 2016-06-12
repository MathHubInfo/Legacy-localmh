from typing import Optional, List
from lmh.utils import exceptions

from lmh.manager.manager import LMHManager
from lmh.programs.program import Program


class SystemManager(object):
    """ A Manager that manages all systems known to lmh. """

    def __init__(self, manager: Optional[LMHManager] = None):
        """ Creates a new SystemManager instance.

        :param manager: Optional. LMHManager() Instance to be used by this SystemManager(). If omitted should be set
        before any actions are registered by setting the manager property.
        """
        
        self.__manager = manager  # type: LMHManager
        self.__systems = []  # type: List[System]
    #
    # Properties
    #
    
    @property
    def manager(self) -> LMHManager:
        """ Gets the LMHManager() instance belonging to this SystemManager() """

        if self.__manager is None:
            raise SystemWithoutManager()
        
        return self.__manager
    
    @manager.setter
    def manager(self, manager : LMHManager) -> None:
        """ Sets the LMHManager instance to be used by this SystemManager().

        :param manager: Manager instance to be set.
        """
        
        self.__manager = manager
    
    #
    # System Functionality
    #
    
    def add(self, system) -> None:
        """ Adds a System to this SystemManager() instance.

        :param system: System to add to this instance
        :type system: System
        """
        
        if not isinstance(system, System):
            raise TypeError("system must be an instance of System()")
        
        if system.name in self:
            raise ValueError('SystemManager() already has a system named %r' % system.name)

        system.register(self)
        self.__systems.append(system)
    
    def __iadd__(self, system):
        """ Same as self.add(system).

        :param system: System to add to this instance.
        :type system: System
        :rtype: SystemManager
        """

        self.add(system)
        return self
    
    def keys(self) -> List[str]:
        """ Returns the names of all systems in this SystemManager. A list of strings representing the names of the
        actions in this SystemManager,
        """
        
        return list(map(lambda s:s.name, self.__systems))
    
    def has_system(self, name: str) -> bool:
        """ Checks if this SystemManager contains a system with the given name.

        :param name: Name of system to search for.
        """
        
        return name in self.keys()
    
    def __contains__(self, name : str) -> bool:
        """ Same as self.has_system(name). """
        
        return self.has_system(name)
    
    def get(self, name: str):
        """ Gets the system with the given name or throws KeyError if it does not exist.
        
        :param name: Name of system to search for.
        :rtype: System
        """
        
        for s in self.__systems:
            if s.name == name:
                return s
        
        raise KeyError
    
    def __getitem__(self, name):
        """ Same as self.get(name).

        :rtype : System
        """

        return self.get(name)
    
    def __call__(self, name : str) -> Program:
        """ Same as self[name](). """

        return self[name]()


class SystemWithoutManager(exceptions.LMHException):
    """ Exception that is thrown when no LMHManager() is bound to an SystemManager() instance. """
    
    def __init__(self):
        """ Creates a new SystemWithoutManager() instance. """
        
        super(SystemWithoutManager, self).__init__('No LMHManager() is bound to this SystemManager() instance')

# avoiding the circular import
from lmh.systems.system import System