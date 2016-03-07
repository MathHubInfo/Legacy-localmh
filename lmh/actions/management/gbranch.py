from lmh.actions import archive
from lmh.actions.management import management
from lmh.archives import gbranch

class GBranchManagerAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that returns the generated branch manager for a selected branch
    """
    
    def __init__(self):
        """
        Creates a new GBranchManagerAction() instance. 
        """
        super(GBranchManagerAction, self).__init__('gbranch-manager', exactly_one = True)
    
    def run_single(self, archive):
        """
        Returns a generatedBranchManager for the given archive
        
        Arguments:
            archive
                LMHArchive() instance to get manager for
        Returns:
            A GeneratedBranchManager() object
        """
        
        return gbranch.GeneratedBranchManager(archive, git=self.manager('git'))

class CreateGBranchAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that creates a new GBranch for an archive and return it   
    """
    
    def __init__(self):
        """
        Creates a new CreateGBranchAction() instance. 
        """
        super(CreateGBranchAction, self).__init__('gbranch-create', exactly_one = True)
    
    def run_single(self, archive, name, path = None):
        """
        Creates a new Generated Branch for a given archive
        
        Arguments:
            archive
                LMHArchive() instance to get manager for
            name
                Name of generated branch to create. 
            path
                Optional. Path to create generated branch at. 
        Returns:
            A GeneratedBranchManager() object
        """
        
        return self.manager['gbranch-manager'].run_single(archive).create(name, path = path)

class GetGBranchAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that gets a single generated branch for an archive
    """
    
    def __init__(self):
        """
        Creates a new GetGBranchAction() instance. 
        """
        super(GetGBranchAction, self).__init__('gbranch-get', exactly_one = True)
    
    def run_single(self, archive, name, path = None):
        """
        Gets a GeneratedBranch instance for a path
        
        Arguments:
            archive
                LMHArchive() instance to install branch of
            name
                Name of branch to get
        Returns:
            A GenertedBranch() object
        """
        
        return self.manager['gbranch-manager'].run_single(archive)[name]

class InstallGBranchAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that installs a generated content branch
    """
    
    def __init__(self):
        """
        Creates a new InstallGBranchAction() instance. 
        """
        super(InstallGBranchAction, self).__init__('gbranch-install', exactly_one = True)
    
    def run_single(self, archive, name):
        """
        Installs a generated content branch
        
        Arguments:
            archive
                LMHArchive() instance to install branch of
            name
                Name of branch to install
        Returns:
            A boolean indicating success or failure
        """
        
        return self.manager['gbranch-get'].run_single(archive, name).install()

class PushGBranchAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that pushes a generated content branch
    """
    
    def __init__(self):
        """
        Creates a new PushGBranchAction() instance. 
        """
        super(PushGBranchAction, self).__init__('gbranch-push', exactly_one = True)
    
    def run_single(self, archive, name):
        """
        Pushes a generated content branch
        
        Arguments:
            archive
                LMHArchive() instance to push branch of
            name
                Name of branch to push
        Returns:
            A boolean indicating success or failure
        """
        
        return self.manager['gbranch-get'].run_single(archive, name).push()

class PullGBranchAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that pulls a generated content branch
    """
    
    def __init__(self):
        """
        Creates a new PullGBranchAction() instance. 
        """
        super(PullGBranchAction, self).__init__('gbranch-pull', exactly_one = True)
    
    def run_single(self, archive, name):
        """
        Pulls a generated content branch
        
        Arguments:
            archive
                LMHArchive() instance to pull branch of
            name
                Name of branch to pull
        Returns:
            A boolean indicating success or failure
        """
        
        return self.manager['gbranch-get'].run_single(archive, name).pull()