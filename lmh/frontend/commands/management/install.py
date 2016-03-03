from lmh.frontend.commands import archive
from lmh.actions import archive as aarchive

class InstallCommand(archive.RemoteArchiveCommand):
    """
    Install a set of archives and their dependencies. 
    """
    
    def __init__(self):
        """
        Creates a new InstallCommand() object. 
        """
        
        super(InstallCommand, self).__init__('install-new', support_all = False)
    
    def _add_args_argparse(self, command):
        """
        Function that should add arguments to the ArgParse object representing
        this command. 
        
        
        Arguments:
            command
                Argparse object representing this command. 
        """
        
        
        deps = command.add_argument_group('Dependency Handling').add_mutually_exclusive_group()
        deps.add_argument('--install-dependencies', dest='deps', action='store_true', default=True, help='Install dependencies of archives. Default. ')
        deps.add_argument('--no-install-dependencies', '-f', dest='deps', action='store_false', help='Do not install dependencies of archives')
        
        rescan = command.add_argument_group('Existing repositories').add_mutually_exclusive_group()
        rescan.add_argument('--rescan-existing', dest='rescan', action='store_true', default=True, help='(Re-)scan installed repositories for missing dependencies. Default. ')
        rescan.add_argument('--ignore-existing', '-i', dest='rescan', action='store_false', help='Ignore existing archives')
        
        confirm = command.add_argument_group('Confirmation').add_mutually_exclusive_group()
        confirm.add_argument('--confirm', dest='confirm', action='store_true', default=True, help='Wait and ask the user after repositories have been resolved. Default. ')
        confirm.add_argument('--no-confirm', '-y', dest='confirm', action='store_false', help='Do not ask user for confirmation and install immediatly')
    
    def call_all(self, archives, parsed_args):
        """
        Calls this command for the given archives with the given arguments. If 
        not overriden by subclass simply calls self.call_single()
        
        Arguments:
            archives
                List of LMHArchive() instances to run the command over
            parsed_args
                An argparse object representing the arguments passed to this 
                command. In order to use this properly use self._build_argparse()
        Returns:
            None, a Boolean or an Integer representing the return code from this 
            command. If the return code is None we assume that the command exited
            normally. 
        """
        
        r = self.manager('install', archives, dependencies = parsed_args.deps, rescan = parsed_args.rescan, confirm = parsed_args.confirm)
        return r != None