from lmh.frontend.commands import archive
from lmh.actions import archive as aarchive

class PullCommand(archive.LocalArchiveCommand):
    """
    Pulls a set of archives and their dependencies. 
    """
    
    def __init__(self):
        """
        Creates a new PullCommand() object. 
        """
        
        super(PullCommand, self).__init__('pull', support_all = True)
    
    def _add_args_argparse(self, command):
        """
        Function that should add arguments to the ArgParse object representing
        this command. 
        
        
        Arguments:
            command
                Argparse object representing this command. 
        """
        
        
        missing = command.add_argument_group('Missing repositories').add_mutually_exclusive_group()
        missing.add_argument('--install-missing', dest='install_missing', action='store_true', default=True, help='Install missing or new dependencies of archives. Default. ')
        missing.add_argument('--no-install-missing', dest='install_missing', action='store_false', help='Do not install dependencies of archives')
        
        deps = command.add_argument_group('Dependency Handling').add_mutually_exclusive_group()
        deps.add_argument('--pull-dependencies', dest='deps', action='store_true', default=True, help='Pull dependencies of archives recursively. Default. ')
        deps.add_argument('--no-pull-dependencies', '-f', dest='deps', action='store_false', help='Do not pull dependencies of archives')
        
        
        generated = command.add_argument_group('Generated Branches').add_mutually_exclusive_group()
        generated.add_argument('--no-install-gbranch', '-n', dest='generated_branches', action='store_false', default=False, help='Ignore generated content branches. Default. ')
        generated.add_argument('--install-gbranch', dest='generated_branches', action='store_true', help='Also pull or install all generated content branches. ')
        
        confirm = command.add_argument_group('Confirmation').add_mutually_exclusive_group()
        confirm.add_argument('--confirm', dest='confirm', action='store_true', default=True, help='Wait and ask the user after repositories have been resolved. Default. ')
        confirm.add_argument('--no-confirm', '-y', dest='confirm', action='store_false', help='Do not ask user for confirmation and update immediatly. ')
    
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
        
        r = self.manager('pull', archives, generated_branches = parsed_args.generated_branches, dependencies = parsed_args.deps, install_missing = parsed_args.install_missing, confirm = parsed_args.confirm)
        
        return r != None