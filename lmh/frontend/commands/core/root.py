from lmh.frontend import command

class RootCommand(command.Command):
    """
    Shows the root directory of the lmh installation. 
    """
    
    def __init__(self):
        """
        Creates a new RootCommand() object. 
        """
        
        super(RootCommand, self).__init__('root')
    
    def call(self):
        """
        Calls this command
        
        Returns:
            None, a Boolean or an Integer representing the return code from this 
            command. If the return code is None we assume that the command exited
            normally. 
        """
        self.manager.logger.log(self.manager('locate'))
        return True