from lmh.archives import archive
from lmh.utils import exceptions
from lmh.utils.caseclass import caseclass


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
    
    def install(self, g):
        """
        Installs this repository locally (without dependencies) or throws
        ArchiveAlreadyInstalled(). 
        
        Arguments:
            g
                A Git() instance which should be used to install the repository
        Returns: 
            LMHRemoteArchive() instance
        """
        
        # if we already exist, abort
        if self.is_local():
            raise ArchiveAlreadyInstalled()
        
        # run the clone command
        g.clone(
            self.instance.local_resolver.to_path(),
            self.resolve_remote(),
            self.resolve_local()
        )
        
        # clear the cache of local repositories because we just installed
        # something
        self.instance.clear_local_cache()
        
        # return the local archive
        return self.to_local_archive()

class NoRemoteArchive(exceptions.LMHException):
    """
    Exception that is thrown when a LMHRemoteArchive() instance is not available locally
    """
    def __init__(self):
        super(NoRemoteArchive, self).__init__('LMHRemoteArchive() instance must be available remotely. ')

class ArchiveAlreadyInstalled(exceptions.LMHException):
    """
    Exception that is thrown when while trying to install an archive it turns out that the repository is 
    already installed. 
    """
    def __init__(self):
        super(ArchiveAlreadyInstalled, self).__init__('LMHRemoteArchive() instance can not be installed: Already exists')