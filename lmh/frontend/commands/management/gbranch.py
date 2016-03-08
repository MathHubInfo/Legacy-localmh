from lmh.frontend.commands import archive
from lmh.archives import gbranch
from lmh.archives import manifest

class GBranchCommand(archive.LocalArchiveCommand):
    """
    Manages generated content branches for a repository
    """
    
    def __init__(self):
        """
        Creates a new GBranchCommand() object. 
        """
        
        super(GBranchCommand, self).__init__('gbranch', single=True)
    
    def _add_args_argparse(self, command):
        """
        Function that should add arguments to the ArgParse object representing
        this command. 
        
        
        Arguments:
            command
                Argparse object representing this command. 
        """

        mode = command.add_argument_group('Mode').add_mutually_exclusive_group()
        
        mode.add_argument('--status', nargs=1, metavar='branch', help='Show status of a generated content branch. ')
        
        mode.add_argument('--init', nargs=1, metavar='branch', default=False, help='Create a new deploy branch, install it locally and push it to the remote. ')
        
        mode.add_argument('--install', nargs=1, metavar='branch', default=False, help='Install deploy branch mentioned in META-INF/MANIFEST.MF from remote. ')
        
        mode.add_argument('--pull', nargs=1, metavar='branch', default=False, help='Pull updates on the generated content branch. ')
        mode.add_argument('--push', nargs=1, metavar='branch', default=False, help='Push updates on the generated content branch. ')
        
        mode.add_argument('--list', help='List all generated content branches available. Default. ', action='store_true')
    
    def call_single(self, archive, *args, parsed_args=None):
        """
        Calls this command with the given arguments on a single archive
        
        Arguments:
            archive
                Archive to run the command over
            parsed_args
                An argparse object representing the arguments passed to this 
                command. In order to use this properly use self._build_argparse()
        Returns:
            A Boolean indicating if the command was succesfull
        """
        
        # get the manager
        manager = self.manager['gbranch-manager'].run_single(archive)
        
        # if we want to create it
        if parsed_args.init:
            branch = parsed_args.init[0]
            try:
                gb = self.manager['gbranch-create'].run_single(archive, branch)
                return gb != False
            except gbranch.BranchAlreadyExists:
                self.manager.logger.fatal('Can not create generated branch %s: A branch with the given name already exists' % branch)
                return False
            except gbranch.PathAlreadyExists:
                self.manager.logger.fatal('Can not create generated branch %s: A folder at that path already exists' % branch)
                return False
            except ValueError as v:
                self.manager.logger.fatal('Can not create generated branch %s: %s' % (branch, v))
                return False
            except manifest.NoManifestFile:
                self.manager.logger.fatal('Can not create generated branch %s: Missing manifest file' % branch)
                return False

        if parsed_args.install:
            branch = parsed_args.install[0]
            try:
                return self.manager['gbranch-install'].run_single(archive, branch) 
            except gbranch.NoSuchGeneratedBranch:
                self.manager.logger.fatal('Can not install generated branch %s: No such generated branch' % branch)
                return False
            except gbranch.BranchAlreadyInstalled:
                self.manager.logger.fatal('Can not install generated branch %s: Branch already installed' % branch)
                return False

        if parsed_args.push:
            branch = parsed_args.push[0]
            try:
                return self.manager['gbranch-push'].run_single(archive, branch) 
            except gbranch.NoSuchGeneratedBranch:
                self.manager.logger.fatal('Can not push generated branch %s: No such generated branch' % branch)
                return False
            except gbranch.BranchNotInstalled:
                self.manager.logger.fatal('Can not push generated branch %s: Branch not installed' % branch)
                return False

        if parsed_args.pull:
            branch = parsed_args.pull[0]
            try:
                return self.manager['gbranch-pull'].run_single(archive, branch) 
            except gbranch.NoSuchGeneratedBranch:
                self.manager.logger.fatal('Can not pull generated branch %s: No such generated branch' % branch)
                return False
            except gbranch.BranchNotInstalled:
                self.manager.logger.fatal('Can not pull generated branch %s: Branch not installed' % branch)
                return False
        
        if parsed_args.status:
            branch = parsed_args.status[0]
            try:
                gbranch = self.manager['gbranch-get'].run_single(archive, branch)
                
                self.manager.logger.log('Name: %s' % gbranch.name)
                self.manager.logger.log('Path: %s' % gbranch.path)
                self.manager.logger.log('Installed: %s' % gbranch.is_installed())
                
                return True
            except gbranch.NoSuchGeneratedBranch:
                self.manager.logger.fatal('Could not display generated branch %s: No such generated branch' % branch)
                return False
        
        for k in manager.keys():
            self.manager.logger.log(k)
        
        return True