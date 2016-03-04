from lmh.utils.clsutils.caseclass import caseclass

import shutil
import os

@caseclass
class System(object):
    """
    Empty BaseClass for systems external to lmh. 
    """
    
    def __init__(self, name, base = None):
        """
        Creates a new System() instance. 
        
        Arguments:
            name
                Name of the system to create
            base
                Optional. Base directory to install system in. Defaults to
                self.manager.locate('systems', name). 
        """
        
        self.name = name
        self.__base = base
        
        self.sysmanager = None
    
    @property
    def base(self):
        """
        Returns the base path belonging to this system. 
        
        Returns:
            a string containing the base path
        """
        
        if self.__base == None:
            return self.manager('locate', 'systems', self.name)
        else:
            return self.__base
    
    def to_path(self, *paths):
        """
        Resolves a path relative to the base directory of this system. 
        
        Arguments:
            *paths
                Paths to resolve
        Returns:
            a string containing the resolved path
        """
        
        return os.path.join(self.base, *paths)
    
    @property
    def manager(self):
        """
        Returns the LMHManager() instance that belongs to this System(). 
        """
        
        return self.sysmanager.manager
    
    def _register(self):
        """
        Protected function called when this System is registered with a
        SystemManager()
        """
        
        pass
        
    
    def register(sysmanager):
        """
        Registers this system with a SystemManager() instance. 
        
        Arguments:
            sysmanager
                SystemsManager Instance to register this system with
        """
        
        self.sysmanager = sysmanager
        
    
    def is_installed(self):
        """
        Checks if this system is currently installed. The default implementation
        checks if the directory self.base exists. 
        
        Returns:
            a boolean indicating if this system is installed or not
        """
        
        return os.path.exists(self.base)
    
    def _install(self):
        """
        Protected Function used to install this system. Should be overridden by subclass.  
        
        Returns:
            a boolean indicating if installation was successfull. 
        """
        
        raise NotImplementedError
    
    def install(self):
        """
        Installs this system if it is not already installed
        
        Returns:
            a boolean indicating if installation was successfull. 
        """
        
        if self.is_installed():
            self.manager.logger.info('System %r is already installed, will not install again. ' % self.name)
            return True
        
        return self._install()
    
    def _update(self):
        """
        Protected Function used to update this system. Should be overridden by subclass.  
        
        Returns:
            a boolean indicating if update was successfull. 
        """
        
        raise NotImplementedError
    
    def update(self):
        """
        Updates this system or throws SystemNotInstalled()
        
        Returns:
            a boolean indicating if update was successfull. 
            
        """
        
        if not self.is_installed():
            raise SystemNotInstalled()
        
        return self._update()
    
    def _remove(self):
        """
        Protected Function used to remove this system. The default 
        implementation just removes the directory self.base. 
        
        Returns:
            a boolean indicating if removal was successfull. 
        """
        
        shutil.rmtree(self.base)
    
    def remove(self):
        """
        Removes this system if it is installed. 
        
        Returns:
            a boolean indicating if removal was successfull. 
        """
        
        if self.is_installed():
            self.manager.logger.info('System %r is not installed, will not remove. ' % self.name)
            return True
        
        return self._remove()
    
    def get(self):
        """
        Returns a program instance representing this System() or throws
        SystemNotInstalled(). Should be overridden by subclass. 
        
        Returns:
            a Program() instance
        """
        
        raise NotImplementedError
    
    def __call__(self):
        """
        Same as self.get()
        """
        return self.get()

class SystemNotInstalled(exceptions.LMHException):
    """
    Exception that is thrown when a system is not installed
    """
    
    def __init__(self):
        """
        Creates a new SystemNotInstalled() instance
        """
        
        super(SystemNotInstalled, self).__init__('System is not installed, can not interact with it')