from lmh.frontend.commands import archive
from lmh.frontend import command
from lmh.logger import escape

from lmh.mathhub.resolvers import remote

class ListCommand(command.Command):
    def _add_args_argparse(self, command):
        """
        Function that should add arguments to the ArgParse object representing
        this command. 
        
        Arguments:
            command
                Argparse object representing this command. 
        """
        
        plain = command.add_argument_group().add_mutually_exclusive_group()
        plain.add_argument('--fancy', dest='plain', action='store_false', default=False, help='Print a fancy tree. Default. ')
        plain.add_argument('--plain', '-p', dest='plain', action='store_true', help='Print a plain list of archives')
    

class LocalListCommand(ListCommand, archive.LocalArchiveCommand):
    """
    Shows a list of locally installed archives. 
    """
    
    def __init__(self):
        """
        Creates a new LocalListCommand() object. 
        """
        
        super(LocalListCommand, self).__init__('ls-local')
    
    def call_single(self, archive):
        """
        Calls this command with the given arguments on a single archive
        
        Arguments:
            archive
                Archive to run the command over
        Returns:
            A Boolean indicating if the command was succesfull
        """
        
        self.manager.logger.log(archive)
        
        return True
    
    def call_all(self, archives, parsed_args=None):
        """
        Calls this command for the given archives with the given arguments. 
        
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
        
        if parsed_args.plain:
            for a in archives:
                self.call_single(a)
        else:
            tree = self.manager('ls-local', archives)
            self.manager.logger.log(tree)
        
        return True

class RemoteListCommand(ListCommand, archive.RemoteArchiveCommand):
    """
    Shows a list of archives that are available remotely. 
    """
    
    def __init__(self):
        """
        Shows a list of remote archives
        """
        
        super(RemoteListCommand, self).__init__('ls-remote')
    
    def call_single(self, archive, *args, parsed_args=None):
        """
        Calls this command with the given arguments on a single archive
        
        Arguments:
            archive
                Archive to run the command over
            *args
                A list of strings passed to this command. In case an argparse 
                object (with the parsed_args) is given, this corresponds to the 
                arguments unknown to argparse. 
            parsed_args
                An argparse object representing the arguments passed to this 
                command. In order to use this properly use self._build_argparse()
        Returns:
            A Boolean indicating if the command was succesfull
        """
        
        if archive.is_local():
            self.manager.logger.log(escape.Green(archive))
        else:
            self.manager.logger.log(escape.Red(archive))
        
        return True
    
    def call_all(self, archives, parsed_args=None):
        """
        Calls this command for the given archives with the given arguments. 
        
        Arguments:
            archives
                List of LMHArchive() instances to run the command over
            *args
                A list of strings passed to this command. In case an argparse 
                object (with the parsed_args) is given, this corresponds to the 
                arguments unknown to argparse. 
            parsed_args
                An argparse object representing the arguments passed to this 
                command. In order to use this properly use self._build_argparse()
        Returns:
            None, a Boolean or an Integer representing the return code from this 
            command. If the return code is None we assume that the command exited
            normally. 
        """
        try:
            
            if parsed_args.plain:
                for a in archives:
                    self.call_single(a)
            else:
                tree = self.manager('ls-remote', archives)
                
                for ic in tree.children:
                    for gc in ic.children:
                        for ac in gc.children:
                            archive = ac.data.data
                            if archive.is_local():
                                ac.data.s = escape.Green(archive.name)
                            else:
                                ac.data.s = escape.Red(archive.name)
            
            self.manager.logger.log(tree)
            
            return True
        
        except remote.NetworkingError:
            self.manager.logger.fatal('Networking Error when attempting to resolve remote archives')
            return False