from lmh.frontend import command

class AliasCommand(command.Command):
    """
    A command that aliases another command
    """
    
    def __init__(self, name, *args, depracated = False):
        """
        Creates a new Alias Command. 
        
        Arguments:
            name
                Name of this command
            *args
                Arguments to prefix the command with
            depracated
                Optional. If set to True, will output a warning that the command is
                depracated everytime it is used. 
            
        """
        
        super(AliasCommand, self).__init__(name)
        
        self.__depracated = depracated
        self.__args = args
        
        self.__strargs = ' '.join(list(map(str, self.__args)))
        self.__doc__ = 'alias for %r' % (self.__strargs, )
    
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
        
        if self.__depracated:
            self.manager.logger.warn('Command %r is deprecated, please use %r instead' % (self.name, self.__strargs))
        
        return self.commander(*(self.__args + args))