from lmh.actions import archive
from lmh.logger import escape

class LocalListAction(archive.LocalArchiveAction):
    """
    An action that prints out all (matching) local archives into the log. 
    """
    
    def __init__(self):
        """
        Creates a new LocalListAction() instance. 
        """
        super(LocalListAction, self).__init__('ls-local', [])
        
    def run_single(self, archive):
        """
        Runs this action on a single remote archive. 
        
        Arguments:
            archive
                LMHArchive() instance to run action on
        """
        
        self.manager.logger.log(str(archive))
        
class RemoteListAction(archive.RemoteArchiveAction):
    """
    An action that prints out all (matching) remote archives into the log. 
    """
    
    def __init__(self):
        """
        Creates a new RemoteListAction() instance. 
        """
        super(RemoteListAction, self).__init__('ls-remote', [])
        
    def run_single(self, archive):
        """
        Runs this action on a single remote archive. 
        
        Arguments:
            archive
                LMHArchive() instance to run action on
        """
        if archive.is_local():
            self.manager.logger.log(escape.Green(str(archive)))
        else:
            self.manager.logger.log(escape.Red(str(archive)))