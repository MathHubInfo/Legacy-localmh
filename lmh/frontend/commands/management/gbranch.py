from lmh.frontend.commands import archive
from lmh.archives import gbranch
from lmh.archives import manifest

class GBranchCommand(archive.LocalArchiveCommand):
    """
    Prints a dependency tree for local archives
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
        
        command.add_argument('branch', nargs='?', help='Name of generated files branch. Mandatory for everything but --list.', default=None)

        mode = command.add_argument_group('Mode').add_mutually_exclusive_group(required=True)
        mode.add_argument('--init', help='Create a new deploy branch, install it locally and push it to the remote. ', action='store_true')
        mode.add_argument('--install', help='Install deploy branch mentioned in META-INF/MANIFEST.MF from remote. ', action='store_true')
        mode.add_argument('--pull', help='Pull updates on the generated content branch. ', action='store_true')
        mode.add_argument('--push', help='Push updates on the generated content branch. ', action='store_true')
        mode.add_argument('--list', help='List all generated content branches available. ', action='store_true')
        mode.add_argument('--status', help='Show status of a generated content branch. ', action='store_true')
    
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
        
        # check what we need to do
        if parsed_args.branch == None and not parsed_args.list:
            self.manager.logger.fatal('Branch argument is required unless --list is given. ')
            return False
        
        # if we want to create it
        if parsed_args.init:
            try:
                return self.manager['gbranch-create'].run_single(archive, parsed_args.branch)
            except gbranch.BranchAlreadyExists:
                self.manager.logger.fatal('Can not create generated branch %s: A branch with the given name already exists' % parsed_args.branch)
                return False
            except gbranch.PathAlreadyExists:
                self.manager.logger.fatal('Can not create generated branch %s: A folder at that path already exists' % args.branch)
                return False
            except ValueError as v:
                self.manager.logger.fatal('Can not create generated branch %s: %s' % (parsed_args.branch, v))
                return False
            except manifest.NoManifestFile:
                self.manager.logger.fatal('Can not create generated branch %s: Missing manifest file' % parsed_args.branch)
                return False

        if parsed_args.install:
            try:
                return self.manager['gbranch-install'].run_single(archive, parsed_args.branch) 
            except gbranch.NoSuchGeneratedBranch:
                self.manager.logger.fatal('Can not install generated branch %s: No such generated branch' % parsed_args.branch)
                return False
            except gbranch.BranchAlreadyInstalled:
                self.manager.logger.fatal('Can not install generated branch %s: Branch already installed' % parsed_args.branch)
                return False

        if parsed_args.push:
            try:
                return self.manager['gbranch-push'].run_single(archive, parsed_args.branch) 
            except gbranch.NoSuchGeneratedBranch:
                self.manager.logger.fatal('Can not push generated branch %s: No such generated branch' % parsed_args.branch)
                return False
            except gbranch.BranchNotInstalled:
                self.manager.logger.fatal('Can not push generated branch %s: Branch not installed' % parsed_args.branch)
                return False

        if parsed_args.pull:
            try:
                return self.manager['gbranch-pull'].run_single(archive, parsed_args.branch) 
            except gbranch.NoSuchGeneratedBranch:
                self.manager.logger.fatal('Can not pull generated branch %s: No such generated branch' % parsed_args.branch)
                return False
            except gbranch.BranchNotInstalled:
                self.manager.logger.fatal('Can not pull generated branch %s: Branch not installed' % parsed_args.branch)
                return False
        
        if parsed_args.status:
            try:
                branch = self.manager['gbranch-get'].run_single(archive, parsed_args.branch)
                
                self.manager.logger.log('Name: %s' % branch.name)
                self.manager.logger.log('Path: %s' % branch.path)
                self.manager.logger.log('Installed: %s' % branch.is_installed())
                
                return True
            except gbranch.NoSuchGeneratedBranch:
                self.manager.logger.fatal('Could not display generated branch %s: No such generated branch' % parsed_args.branch)
                return False
        
        for k in manager.keys():
            self.manager.logger.log(k)
        
        return True