from lmh.utils import exceptions
from lmh.archives import archive

from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class LMHRemoteArchive(archive.LMHArchive):
    """
    Represents an LMH Archive that is remotely available. 
    """
    
    def __init__(self, instance, group, name):
        """
        Creates a new remote archive instance. 
        
        Arguments:
            instance
                MathHubInstance() representing the original source of this 
                Archive. 
            group
                Name of the group this archive belongs to
            Name
                The name of this archive
        """
        
        super(LMHRemoteArchive, self).__init__(instance, group, name)
        
        if not self.is_remote():
            raise NoRemoteArchive()
    
    def __repr__(self):
        """
        Returns a string representation of this LMHRemoteArchive. 
        
        Returns: 
            a string
        """
        
        return 'LMHRemoteArchive(%r, %r)' % (self.instance, str(self))

class NoRemoteArchive(exceptions.LMHException):
    """
    Exception that is thrown when a LMHRemoteArchive() instance is not available locally
    """
    def __init__(self):
        super(NoRemoteArchive, self).__init__('LMHRemoteArchive() instance must be available remotely. ')