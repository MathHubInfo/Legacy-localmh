from lmh.frontend import command

class AboutCommand(command.Command):
    """
    Display information about lmh itself
    """
    
    def __init__(self):
        """
        Creates a new AboutCommand() object. 
        """
        
        super(AboutCommand, self).__init__('about')
    
    def call(self):
        """
        Calls this command
        
        Returns:
            None, a Boolean or an Integer representing the return code from this 
            command. If the return code is None we assume that the command exited
            normally. 
        """
        
        version = self.manager('info', 'version')
        license = self.manager('info', 'license')
        
        self.manager.logger.log('%s\n\n%s' % (version, license))
        
        return True