from lmh.utils import exceptions
import argparse

from typing import List, Optional, Dict, Any, Union

from lmh.manager.manager import LMHManager


class Command(object):
    """ A Command represents a command that can be run from the Frontend of
    lmh. """
    
    def __init__(self, name: str):
        """ Creates a new Command() object.

        :param str: Name of this command.
        """

        self.__name = name  # type: str

        self.__commander = None  # type: LMHCommander

    @property
    def name(self) -> str:
        """ Returns the name of this Command. """

        return self.__name
    
    @property
    def commander(self):
        """ Gets the LMHCommander() instance used by this Command() or throws
        CommandWithoutCommander.

        :rtype: LMHCommander
        """

        # if it is empty
        if self.__commander is None:
            raise CommandWithoutCommander()

        return self.__commander
    
    @property
    def manager(self) -> LMHManager:
        """ Gets the LMHManager instance used by this Command() or throws
        CommandWithoutCommander or CommanderWithoutManager when appropriate.
        """
        
        return self.commander.manager
    
    def _register(self) -> None:
        """ Protected Function that is called when this command is
        registered. """

        pass
        
    def register(self, commander) -> None:
        """ Called when this command is registered with a commander.

        :param commander: Commander that this command is registered with.
        :type commander: LMHCommander
        """

        self.__commander = commander
        self._register()
    
    def _build_argparse(self, subparsers: argparse._ActionsContainer) -> None:
        """ Function that adds a new subparser representing this parser. May
        throw NotImplementedError if another parsing libary is used.
        
        :param subparsers: Argparse subparsers object to add parsers to.
        """
        
        raise NotImplementedError

    def call(self, *args: List[str],
             parsed_args: Optional[argparse.Namespace]=None)\
            -> Union[None, bool, int]:
        """
        Calls this command with the given arguments.

        :parm args: A list of strings passed to this command. In case an
        argparse object (with the parsed_args) is given, this corresponds to
        the arguments unknown to argparse.
        :param parsed_args: An argparse object representing the arguments
        passed to this command. In order to use this properly use
        self._build_argparse(). May be omitted from subclasses if not needed.
        :return: None, a Boolean or an Integer representing the return code
        from this command. If the return code is None we assume that the
        command exited normally.
        """
        
        raise NotImplementedError
    
    def __call__(self, *args: List[Any], **kwargs: Dict[str, Any])\
            -> Union[None, bool, int]:
        """ Same as self.call(*args, **kwargs). """

        return self.call(*args, **kwargs)

class CommandWithoutCommander(exceptions.LMHException):
    """ Exception that is thrown when no LMHCommander() is bound to an
    Command() instance.  """
    
    def __init__(self):
        """ Creates a new CommandWithoutCommander() instance. """
        
        super(CommandWithoutCommander, self).__init__('No LMHCommander() ' +
                                                      'is bound to this ' +
                                                      'Command() instance')

# to avoid cyclic imports
from lmh.frontend.commander import LMHCommander

__all__ = ["Command", "CommandWithoutCommander"]
