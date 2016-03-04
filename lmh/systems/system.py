from lmh.utils.clsutils.caseclass import caseclass

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
                Base directory to install system in. 
        """
        
        self.name = name
        self.base = base
        
        self.sysmanager = None
    
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
        Checks if this system is currently installed. 
        
        Returns:
            a boolean indicating if this system is installed or not
        """
        
        raise NotImplementedError
    
    def install(self):
        """
        Installs this system if it is not already installed
        
        Returns:
            a boolean indicating if installation was successfull. 
            Should be overridden by subclass.  
        """
        
        raise NotImplementedError
    
    def update(self):
        """
        Updates this system if it is not already installed
        
        Returns:
            a boolean indicating if update was successfull. 
            Should be overridden by subclass.  
        """
        
        raise NotImplementedError
    
    def remove(self):
        """
        Removes this system if it is not already installed
        
        Returns:
            a boolean indicating if removal was successfull. 
            Should be overridden by subclass.  
        """
        
        raise NotImplementedError
    
    def get(self):
        """
        Returns a program instance representing this System() or throws
        SystemNotInstalled(). Should be overridden by subclass. 
        
        Returns:
            a Program() instance
        """
        
        raise NotImplementedError

class SystemNotInstalled(exceptions.LMHException):
    """
    Exception that is thrown when a system is not installed
    """
    
    def __init__(self):
        """
        Creates a new SystemNotInstalled() instance
        """
        
        super(SystemNotInstalled, self).__init__('System is not installed, can not interact with it')