from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class System(object):
    """
    Empty BaseClass for systems external to lmh. 
    """
    
    def is_installed(self):
        """
        Checks if this system is currently installed. 
        """
        
        raise NotImplementedError
    
    def install(self):
        """
        Installs this system if not already installed
        """
        pass
    
    def update(self):
        """
        Updates this system if not already up-to-date. 
        """
        pass
    
    def remove(self, manager):
        """
        Removes this system if it is not already installed. 
        """
        pass
    
    def get(self):
        """
        Gets a program() instance representing this system
        """
        pass