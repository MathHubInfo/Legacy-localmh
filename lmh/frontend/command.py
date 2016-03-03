from lmh.utils import exceptions

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
        
        self.__commander = None
    
    @property
    def commander(self):
        """
        Gets the LMHCommander() instance used by this Command() or throws
        CommandWithoutCommander. 
        
        Returns:
            An LMHCommander() instance
        """
        
        if self.__commander == None:
            raise CommandWithoutCommander()
        
        return self.__commander
    
    @property
    def manager(self):
        """
        Gets the LMHManager instance used by this Command() or throws
        CommandWithoutCommander or CommanderWithoutManager when appropriate. 
        
        Returns:
            A LMHManager() instance
        """
        
        return self.commander.manager
    
    
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
        self.__commander = commander
        self._register()
    
    def _build_argparse(self, subparsers):
        """
        Function that adds a new subparser representing this parser. 
        May throw NotImplementedError if another parsing libary is used. 
        
        
        Arguments:
            subparsers
                Argparse subparsers object to add parsers to
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

class CommandWithoutCommander(exceptions.LMHException):
    """
    Exception that is thrown when no LMHCommander() is bound to an Command() instance
    """
    
    def __init__(self):
        """
        Creates a new CommandWithoutCommander() instance
        """
        
        super(CommanderWithoutManager, self).__init__('No LMHCommander() is bound to this Command() instance')