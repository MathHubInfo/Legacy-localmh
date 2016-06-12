import os
import shutil
from typing import Optional, List

from lmh.utils import exceptions
from lmh.utils.caseclass import CaseClass
from lmh.systems.manager import SystemManager
from lmh.manager.manager import LMHManager
from lmh.programs.program import Program


class System(CaseClass):
    """ Empty BaseClass for systems external to lmh. """
    
    def __init__(self, name: str, base: Optional[str] = None):
        """ Creates a new System() instance.

        :param name: Name of the system to create.
        :param base: Optional. Base directory to install system in. Defaults to self.manager.locate('systems', name).
        """

        super(System, self).__init__(name, base)
        
        self.name = name  # type: str
        self.__base = base  # type: str

        self.system_manager = None  # type: SystemManager
    
    @property
    def base(self) -> str:
        """ Returns the base path belonging to this system. """
        
        if self.__base is None:
            return self.manager('locate', 'systems', self.name)
        else:
            return self.__base
    
    def to_path(self, *paths: List[str]) -> str:
        """ Resolves a path relative to the base directory of this system.

        :param paths: Paths to resolve.
        :return: a string containing the resolved path
        """

        return os.path.join(self.base, *paths)
    
    @property
    def manager(self) -> LMHManager:
        """ Returns the LMHManager() instance that belongs to this System(). """

        return self.system_manager.manager
    
    def _register(self) -> None:
        """ Function called when this System is registered with a SystemManager() """
        
        pass

    def register(self, system_manager : SystemManager) -> None:
        """ Registers this system with a SystemManager() instance.

        :param system_manager: SystemsManager Instance to register this system with
        """

        # TODO: Do we need to call a .register() function?
        self.system_manager = system_manager

    def is_installed(self) -> bool:
        """ Checks if this system is currently installed. The default implementation checks if the directory self.base
        exists. """
        
        return os.path.exists(self.base)
    
    def _install(self) -> bool:
        """ Protected Function used to install this system. Should be overridden by subclass. """
        
        raise NotImplementedError
    
    def install(self) -> bool:
        """ Installs this system if it is not already installed

        :return: a boolean indicating if installation was successful.
        """
        
        if self.is_installed():
            self.manager.logger.info('System %r is already installed, will not install again. ' % self.name)
            return True
        
        return self._install()
    
    def _update(self) -> bool:
        """ Protected Function used to update this system. Should be overridden by subclass. """
        
        raise NotImplementedError
    
    def update(self) -> bool:
        """ Updates this system or throws SystemNotInstalled()

        :return: a boolean indicating if update was successful.
        """
        
        if not self.is_installed():
            raise SystemNotInstalled()
        
        return self._update()
    
    def _remove(self) -> bool:
        """ Protected Function used to remove this system. The default implementation just removes the directory
        self.base. """

        try:
            shutil.rmtree(self.base)
        except shutil.Error:
            return False

        return True

    def remove(self) -> bool:
        """ Removes this system if it is installed.

        :return: a boolean indicating if removal was successful.
        """
        
        if self.is_installed():
            self.manager.logger.info('System %r is not installed, will not remove. ' % self.name)
            return True
        
        return self._remove()
    
    def get(self) -> Program:
        """ Returns a program instance representing this System() or throws SystemNotInstalled().
        Should be overridden by subclass. """
        
        raise NotImplementedError
    
    def __call__(self) -> Program:
        """ Same as self.get(). """
        return self.get()


class SystemNotInstalled(exceptions.LMHException):
    """ Exception that is thrown when a system is not installed. """
    
    def __init__(self):
        """ Creates a new SystemNotInstalled() instance. """
        
        super(SystemNotInstalled, self).__init__('System is not installed, can not interact with it')