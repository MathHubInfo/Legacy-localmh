from lmh.frontend.commands import archive
from lmh.logger import escape

class LocalListCommand(archive.LocalArchiveCommand):
    """
    Shows a list of local repositories
    """
    
    def __init__(self):
        """
        Creates a new LocalListCommand() object. 
        """
        
        super(LocalListCommand, self).__init__('ls-local')
    
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
        
        self.manager.logger.log(archive)
        
        return True

class RemoteListCommand(archive.RemoteArchiveCommand):
    """
    Shows the depdendency tree of local repositories
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