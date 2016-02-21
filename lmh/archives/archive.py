from lmh.utils import exceptions
from lmh.mathhub.resolvers import resolver

from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class LMHArchive(object):
    """
    Represents an LMH Archive that can be local or remote. 
    """
    
    def __init__(self, instance, group, name):
        """
        Creates a new archive instance. 
        
        Arguments:
            instance
                MathHubInstance() representing the original source of this 
                Archive. 
            group
                Name of the group this archive belongs to
            Name
                The name of this archive
        """
        
        self.instance = instance
        self.group = group
        self.name = name
    
    def __repr__(self):
        """
        Returns a string representation of this LMHArchive. 
        
        Returns: 
            a string
        """
        
        return 'LMHArchive(%r, %r)' % (self.instance, str(self))
    
    def __str__(self):
        """
        Returns a string representing this LMHArchive
        
        Returns: 
            a string
        """
        
        return '%s/%s' % (self.group, self.name)
        
    def resolve_local(self):
        """
        Resolves the local path to this archive or throws RepositoryNotFound()
        
        Returns:
            A string representing the local path to this archive
        """
        
        return self.instance.get_local_path(self.group, self.name)
    
    def is_local(self):
        """
        Checks if this archive is available locally, i. e. if it is installed. 
        
        Returns:
            A boolean indicating if this archive is installed locally. 
        """
        
        try:
            self.resolve_local()
            return True
        except resolver.RepositoryNotFound:
            return False
    
    def to_local_archive(self):
        """
        Returns a LMHLocalArchive() instance representing this archive. 
        """
        
        from lmh.archives import local
        return local.LMHLocalArchive(self.instance, self.group, self.name)
    
    def resolve_remote(self):
        """
        Resolves the remote path to this archive or throws RepositoryNotFound()
        
        Returns:
            A string representing the remote path to this archive
        """
        
        return self.instance.get_remote_path(self.group, self.name)
    
    def is_remote(self):
        """
        Checks if this archive is available remotely, i. e. if it can be installed
        via git. 
        
        Returns:
            A boolean indicating if this archive is installed locally. 
        """
        
        try:
            self.resolve_remote()
            return True
        except resolver.RepositoryNotFound:
            return False
    
    def to_remote_archive(self):
        """
        Returns a LMHRemoteArchive() instance representing this archive. 
        """
        
        from lmh.archives import remote
        return remote.LMHRemoteArchive(self.instance, self.group, self.name)