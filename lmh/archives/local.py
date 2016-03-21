from lmh.utils import exceptions
from lmh.archives import archive, manifest
from lmh.mathhub.resolvers import resolver

import os.path

from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class LMHLocalArchive(archive.LMHArchive):
    """
    Represents an LMH Archive that is locally available. 
    """
    
    def __init__(self, instance, group, name):
        """
        Creates a new local archive instance. 
        
        Arguments:
            instance
                MathHubInstance() representing the original source of this 
                Archive. 
            group
                Name of the group this archive belongs to
            Name
                The name of this archive
        """
        
        super(LMHLocalArchive, self).__init__(instance, group, name)
        
        if not self.is_local():
            raise NoLocalArchive() 
        
        try:
            self.__base = super(LMHLocalArchive, self).resolve_local()
        except resolver.RepositoryNotFound:
            raise NoLocalArchive()
        
        self.__manifest = None
    
    def __repr__(self):
        """
        Returns a string representation of this LMHLocalArchive. 
        
        Returns: 
            a string
        """
        
        return 'LMHLocalArchive(%r, %r)' % (self.instance, str(self))
    
    def to_path(self, *paths):
        """
        Resolves a path relative to the base directory of this archive.
        
        Arguments:
            *paths
                Paths to resolve
        Returns:
            A string containing the resolved path
        """
        
        return os.path.join(self.__base, *paths)
        
    #
    # MANIFEST
    #
    
    @property
    def manifest(self):
        """
        Gets a Manifest() instance for this archive or throws NoManifestFile()
        
        Returns:
            A Manifest() instance for this repository. 
        """
        
        if self.__manifest != None:
            return self.__manifest
        
        self.__manifest = manifest.Manifest(self.to_path("META-INF", "MANIFEST.MF"))
        
        return self.__manifest
    
    #
    # DEPENDENCIES
    #
    
    @property
    def dependencies(self):
        """
        Gets the dependencies of this archive
        
        Arguments:
            manager
                Optional. Manager instance to search dependencies in. 
        
        Returns:
            A list of LMHArchive() instances representing the dependencies
        """
        
        dependencies = set()
        
        # if we have no dependency key, return the empty list
        if not 'dependencies' in self.manifest:
            return []
        
        for d in (self.manifest['dependencies']).split(','):
            if '/' in d:
                dependencies.add((d[:d.index("/")].strip(), d[d.index("/")+1:].strip()))
            elif d.strip() != '':
                raise MalformedDependenciesError()
        
        return [archive.LMHArchive(self.instance, g, n) for (g, n) in dependencies]
    
    @dependencies.setter
    def dependencies(self, dependencies):
        """
        Sets the dependencies of this archive
        
        Arguments:
            dependencies
                A list of strings or LMHArchive instances that should be written
                to the MANIFEST.MF file
        """
        
        self.manifest['dependencies'] = ','.join(list(map(str, dependencies)))
    
    #
    # MANAGMENET ACTIONS
    #
    def remote_status(self, git):
        """
        Gets the remote status of this repository. 
        
        Arguments:
            git
                a Git() instance to be used to resolve the remote status
        Returns:
             one of 'ok', 'pull', 'push', 'divergence' or None indicating the
             status of the remote
        """
        
        return git.get_remote_status(self.__base)
    
    def pull(self, git):
        """
        Pulls this archive from the remote. 
        
        Arguments:
            git
                a Git() instance to pull the archive
        Returns:
            a boolean indicating if the pull was successfull
        """
        
        return git.pull(self.resolve_local())
    
    def push(self, git):
        """
        Pushes this archive to the remote. 
        
        Arguments:
            git
                a Git() instance to push the archive
        Returns:
            a boolean indicating if the push was successfull
        """
        
        return git.push(self.resolve_local())
    
    #
    # LOCAL ARCHIVE RESOLUTION
    #
    def resolve_local(self):
        """
        Resolves the local path to this archive. 
        """
        
        return self.__base
    
    def to_local_archive(self):
        """
        Returns a LMHLocalArchive() instance representing this archive. 
        """
        
        return self
    

class NoLocalArchive(exceptions.LMHException):
    """
    Exception that is thrown when a LMHLocalArchive() instance is not available locally
    """
    def __init__(self):
        super(NoLocalArchive, self).__init__('LMHLocalArchive() instance must be available locally. ')

class MalformedDependenciesError(exceptions.LMHException):
    """
    Exception that is thrown when a LMHLocalArchive() has malformed dependencies
    """
    def __init__(self):
        super(NoManifestFile, self).__init__('Malformed Dependencies found in the MANIFEST.MF file')