from lmh.frontend import command
import argparse
class LegacyCommand(command.Command):
    """
    A command in the old format. Depracted, to be removed once no longer needed
    """
    
    def __init__(self, name):
        """
        Creates a new LegacyCommand() object. 
        
        Arguments:
            name
                Name of this command
        """
        
        super(LegacyCommand, self).__init__(name)
        
        self.__module = getattr(getattr(__import__("lmh.commands."+name), "commands"), name)
        self.__command = self.__module.Command()
    
    def _build_argparse(self, subparsers):
        """
        Function that adds a new subparser representing this parser. 
        
        Arguments:
            subparsers
                Argparse subparsers object to add parsers to
        """
        
        # Create the sub parser
        new_parser = subparsers.add_parser(self.name, help=self.__command.help, description=self.__command.help, formatter_class=LMHFormatter, add_help=self.__command.allow_help_arg)

        # and add some arguments.
        self.__command.add_parser_args(new_parser)
    
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
        
        return self.__command.do(parsed_args, args)
class LMHFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass