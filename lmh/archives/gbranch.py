from lmh.archives import manifest
from lmh.utils import exceptions, fileio

import os.path

class GeneratedBranchManager(object):
    """
    A manager that can install, remove and create generated branches
    """
    
    def __init__(self, archive, git):
        """
        Creates a new GeneratedBranchManager() instance
        
        Arguments:
            archive
                LMHLocalArchive() instance to manage generated branches on
            git
                Git() program to work with
        """
        
        self.archive = archive.to_local_archive()
        self.__branches = {}
        self.git = git
    
    def keys(self):
        """
        Gets a list of generated branch names. 
        
        Returns:
            a list containing the names of all generated branches for this 
            GeneratedBranchManager()
        """
        
        kd = []
        
        # load the string representing the branches
        try:
            bstr = self.archive.manifest['generated_branches']
        except KeyError:
            bstr = ''
        except manifest.NoManifestFile:
            bstr = ''
        
        # and make sure to split it properly
        for k in bstr.split(' '):
            if ':' in k:
                kd.append(k[:k.index(':')].strip())
            else:
                kd.append(k.strip())
        
        # and return
        return list(filter(lambda k:k!='', kd))
    
    def get(self, name):
        """
        Gets a GeneratedBranch with the given name or throws 
        NoSuchGeneratedBranch()
        
        Arguments:
            name
                Name of the generatedBranch to get
        Returns:
            A GeneratedBranch() instance
        """
        
        if name in self.__branches.keys():
            return self.__branches[name]
        
        self.__branches[name] = GeneratedBranch(self, name)
        return self.__branches[name]
    
    def __getitem__(self, name):
        """
        Same as self.get(name)
        """
        return self.get(name)
    
    def create(self, name, path = None):
        """
        Creates a generated branch with the given name or throws 
        
        Arguments:
            name
                Name of generated branch to create
            path
                Optional. Path to create generated branch at. Defaults to name. 
        
        Returns a new GeneratedBranch() instance or False in case creation failed. 
        """
        
        # make sure the branch does not exist by catching NoSuchGeneratedBranch
        try:
            self.get(name)
            raise BranchAlreadyExists()
        except NoSuchGeneratedBranch:
            pass
        
        # If path is None, default to the name
        if path == None:
            path = name
        
        # Get the paths
        rpath = self.archive.to_path()
        bpath = self.archive.to_path(path)
        
        # if the path already exists we can not continue
        if os.path.isdir(bpath):
            raise PathAlreadyExists()
        
        # update the gitignore
        gi_path = self.archive.to_path('.gitignore')
        
        # either create or append
        if os.path.isfile(gi_path):
            gi_c = fileio.read_file(gi_path)
        else:
            gi_c = ''
        
        gi_c += '/%s\n' % (path,)
        
        if not fileio.write_file(gi_path, gi_c):
            raise ValueError('unable to write .gitignore')
        
        # make a string representing a path
        mns = name if name == path else ('%s:%s' % (name, path))
        
        try:
            gen_branch_current = self.archive.manifest['generated_branches']
        except KeyError:
            gen_branch_current = ''
        
        # update manifest with the name
        self.archive.manifest['generated_branches'] = ('%s %s' % (gen_branch_current, mns)).strip()
        
        # make an orphaned branch
        if not self.git.make_orphan_branch(rpath, name):
            return False
        
        # push it to origin
        if not self.git.do(rpath, 'push', '-u', 'origin', name):
            return False
        
        # get and install it
        gbranch = self.get(name)
        
        # install it
        if not gbranch.install():
            return False

        # change the commit message
        if not self.git.do(bpath, 'commit', '--amend', '--allow-empty', '-m', 'Created generated content branch %s at %s' % (name, path)):
            return False

        # and push it.
        if not self.git.do(bpath, 'push', '--force', 'origin', name):
            return False
        
        return gbranch
    
    def install_all(self, pull = False):
        """
        Installs all generated branches that are not yet installed. 
        
        Arguments:
            pull
                By default nothing is done with already installed generated 
                branches. If set to True, updates all existing generted 
                branches.  
        
        Returns:
            a list of pairs (n, s) indicating the name of each generated branch 
            and if its installation was successfull or not
        """
        
        status = []
        
        # iterate through all the branches
        for k in self.keys():
            gb = self[k]
            
            # if a branch is not installed, try to install it
            if not gb.is_installed():
                try:
                    rt = gb.install()
                    status.append((k, rt))
                except gbranch.BranchAlreadyInstalled:
                    status.append((k, False))
            elif pull:
                try:
                    rt = gb.pull()
                    status.append((k, rt))
                except gbranch.BranchAlreadyInstalled:
                    status.append((k, False))
                
        
        # return the code of statusses
        return status
        
class GeneratedBranch(object):
    """
    Represents a single Generated Branch
    """
    
    def __init__(self, manager, name):
        """
        Represents a generated branch with the given name and path. 
        
        Arguments:
            manager
                A GeneratedBranchManager() that manages all existing GeneratedBranches
        """
        
        # Load some of the properties
        self.__manager = manager
        self.__archive = manager.archive
        self.__git = manager.git
        
        # Set the name
        self.name = name 
        
        # and try to get the path
        try:
            paths = self.__archive.manifest['generated_branches'].split(' ')
            for p in paths:
                if p == name:
                    self.path = name
                    break
                elif p.contains(':') and p[:p.index(':')] == name:
                    self.path = p[p.index(':')+1:]
                    break
            
        except manifest.NoManifestFile:
            raise NoSuchGeneratedBranch()
        except KeyError:
            raise NoSuchGeneratedBranch()
        
        self.__rpath = self.__archive.to_path()
        self.__bpath = self.__archive.to_path(self.path)
    
    def __get_path(self):
        """
        Private function used to get the path of this generated branch. 
        
        Returns:
            the name of the folder this branch should be installed in. 
        """
        
        braw = self.__archive.manifest['generated_branches'].split(' ')
        for b in braw:
            b = b.strip()
            if ':' in b:
                if b[:b.index(':')] == self.name:
                    return b[b.index(':')+1:]
            else:
                if b == self.name:
                    return b
        raise NoSuchGeneratedBranch()
    
    def is_installed(self):
        """
        Returns a boolean indicating if this generated branch is installed. 
        
        Returns:
            a boolean
        """
        
        return os.path.isdir(self.__bpath)
    
    def install(self):
        """
        Installs this generated branch or throws BranchAlreadyInstalled() if it
        already is. 
        """
        
        if self.is_installed():
            raise BranchAlreadyInstalled()
        
        # read the origin url
        (origin, e) = self.__git.do_data(self.__rpath, 'config', '--local', '--get', 'remote.origin.url')
        
        # ensure the remote branch exists
        # and make sure it is tracked locally
        if not self.__git.do(self.__rpath, 'rev-parse', '--verify', '--quiet', self.name):
            if not self.__git.do(self.__rpath, 'branch', self.name, '--track', 'origin/%s' % self.name):
                return False

        # Clone it shared
        if not self.__git.do(self.__rpath, 'clone', self.__rpath, self.__bpath, '--shared', '-b', self.name):
            return False

        # set up .git/objects/info/alternates relatively
        if not fileio.write_file(os.path.join(self.__bpath, '.git', 'objects', 'info', 'alternates'), '../../../.git/objects'):
            return False

        # set the origin
        if not self.__git.do(self.__bpath, 'remote', 'set-url', 'origin', origin.rstrip('\n')):
            return False
        
        # and delete the branch from our repository
        return self.__git.do(self.__rpath, 'branch', '-D', self.name)
    
    def __housekeeping(self):
        """
        Performs git housekeeping tasks that ensure this GeneratedBranch does not
        waste disk space. 
        
        Returns:
            A Boolean indicating if the housekeeping task was successfull. 
        """
        
        if not self.__git.do(self.__bpath, 'gc', '--auto'):
            return False
        
        return self.__git.do(self.__rpath, 'gc', '--auto')
        
    
    def pull(self):
        """
        Pulls this generated branch or throws BranchNotInstalled() if it is
        not installed. 
        
        Returns:
            A boolean indicating if it was successfull or not. 
        """
        
        if not self.is_installed():
            raise BranchNotInstalled()
        
        # Fetch origin in the clone repo.
        if not self.__git.do(self.__rpath, 'fetch', '--depth', '1', 'origin', self.name):
            return False

        # Hard reset this repository.
        if not self.__git.do(self.__bpath, 'reset', '--hard', 'origin/%s' % self.name):
            return False

        # do some housekeeping in both repos
        return self.__housekeeping()
    
    def push(self):
        """
        Pushes this generated branch or throws BranchNotInstalled() if it is
        not installed. 
        
        Returns:
            A boolean indicating if it was successfull or not. 
        """
        
        if not self.is_installed():
            raise BranchNotInstalled()
        
        # add all the changes.
        if not self.__git.do(self.__bpath, 'add', '-A', '.'):
            return False

        # commit them.
        if not self.__git.do(self.__bpath, 'commit', '--amend', '--allow-empty', '-m', 'Update generated content'):
            return False

        # and force push them.
        if not self.__git.do(self.__bpath, 'push', '--force', 'origin', self.name):
            return False
        
        # do some housekeeping in both repos
        return self.__housekeeping()

class NoSuchGeneratedBranch(exceptions.LMHException):
    """
    Exception that is thrown when no generated branch with the given name does
    not exist
    """
    def __init__(self):
        super(NoSuchGeneratedBranch, self).__init__('Specefied Generated Branch does not exist')

class BranchNotInstalled(exceptions.LMHException):
    """
    Exception that is thrown when the generated branch is not installed. 
    """
    def __init__(self):
        super(BranchNotInstalled, self).__init__('Specefied Generated Branch is not installed')

class BranchAlreadyExists(exceptions.LMHException):
    """
    Exception that is thrown when a generated branch already exists. 
    """
    def __init__(self):
        super(BranchAlreadyExists, self).__init__('A generated branch with the given name already exists')

class PathAlreadyExists(exceptions.LMHException):
    """
    Exception that is thrown when a generated branch can not be created at the given path
    """
    def __init__(self):
        super(PathAlreadyExists, self).__init__('A folder with the given path already exists')

class BranchAlreadyInstalled(exceptions.LMHException):
    """
    Exception that is thrown when the generated branch is already installed. 
    """
    def __init__(self):
        super(BranchAlreadyInstalled, self).__init__('Specefied Generated Branch is already installed')