from lmh.actions import action
from lmh.utils import fileio

class InfoAction(action.Action):
    """
    An action that returns information about LMH Version as well as license
    """
    
    def __init__(self):
        """
        Creates a new InfoAction() instance
        """
        super(InfoAction, self).__init__('info')
    
    
    def license(self):
        """
        Returns license information about lmh
        
        Returns:
            a string containing the license text of lmh
        """
        
        # just read the license file
        return fileio.read_file(self.manager('locate', 'spec', 'license'))
    
    def version(self):
        """
        Returns version information of lmh. 
        """
        
        version = fileio.read_file(self.manager('locate', 'spec', 'version')).strip()
        try:
            git_version = self.manager('git').do_data(self.manager('locate'), 'rev-parse', 'HEAD')[0].rstrip()
        except:
            git_version = None
        
        # Return the current version of lmh
        return 'lmh, version %s %s' % (version, '(git %s)' % (git_version,) if git_version else '(not under git control)') 
    
    def run(self, mode):
        """
        Runs this action, returns a string text representing lmh
        
        Arguments: 
            mode
                One of 'license', 'version'. Returns information about
                the selected topic. 
        Returns: 
            An Arbritrary object representing the result of the action
        """
        
        if mode == 'license':
            return self.license()
        elif mode == 'version':
            return self.version()
        else:
            raise ValueError('mode must be one of %r %r, not %r' % ('license', 'version', mode))