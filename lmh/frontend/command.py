class Command(object):
    """
    A Command represents a command that can be run from the Frontend of lmh
    """
    
    def __init__(self, name):
        """
        Creates a new Command() object. 
        
        Arguments:
            name
                Name of this Command
        """
        self.name = name
        
        self.commander = None
        self.manager = None
    
    def _register(self):
        """
        Protected Function that is called when this command is registered. 
        """
        pass
        
    def register(self, commander):
        """
        Called when this command is registered with a commander. 
        
        Arguments:
            commander
                Commander that this command is registered with
        """
        self.commander = commander
        self.manager = self.commander.manager
        self._register()
    
    def _build_argparse(self):
        """
        Function called by the commander when an argparse instance representing
        this command should be built. May throw NotImplementedError if another
        parsing libary is used. 
        
        Returns:
            An argparse instance
        """
        
        raise NotImplementedError

    def call(self, *args, parsed_args=None):
        """
        Calls this command with the given arguments. 
        
        Arguments:
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
        
        raise NotImplementedError
    
    def __call__(self, *args, **kwargs):
        """
        Same as self.call(*args, **kwargs)
        """
        return self.call(*args, **kwargs)