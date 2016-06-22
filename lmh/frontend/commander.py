from typing import Optional, List, Any, Tuple

from lmh.manager.manager import LMHManager
from lmh.utils.exceptions import LMHException
from lmh.frontend.command import Command

import argparse
import inspect
import os


class LMHCommander(object):
    """ Manages all commands used by LMH. """
    
    def __init__(self, manager: Optional[LMHManager] = None,
                 base: Optional[str] = None):
        """ Creates a new LMHCommander() instance.
        
        :param manager: Optional. LMHManager() object used by this Commander.
        If omitted should be set before commands are registered by setting the
        manager property.
        :param base: Optional. Base relative to which this commander should run
        commands for.
        """
        
        self.__manager = manager  # type: Optional[LMHManager]
        
        self.__commands = []  # type: List[Command]
        self.__base = os.getcwd() if base == None else base  # type: str

    @property
    def base(self) -> str:
        """ Returns the current base for repository resolution. """

        return self.__base
    
    @property
    def manager(self) -> LMHManager:
        """ Gets the LMHManager instance belonging to this Commander() or throws
        CommanderWithoutManager().
        """
        
        if self.__manager == None:
            raise CommanderWithoutManager()
        
        return self.__manager
    
    @manager.setter
    def manager(self, manager: LMHManager) -> None:
        """ Sets the Manager instance to be used by this Commander().
        
        :param manager:  Manager instance to be set.
        """
        
        self.__manager = manager
    
    def add(self, cmd: Command) -> None:
        """ Adds a Command to this LMHCommander() instance.
        
        :param cmd: Command that should be added to this LMHCommander().
        """
        
        if not isinstance(cmd, Command):
            raise TypeError("cmd must be an instance of Command()")
        
        if cmd.name in self:
            raise ValueError('LMHCommander() already has a command named %r' % cmd.name)
        
        cmd.register(self)
        self.__commands.append(cmd)
    
    def __iadd__(self, cmd: Command):
        """ Same as self.add(cmd).

        :rtype: LMHCommander
        """

        self.add(cmd)
        return self
    
    def keys(self) -> List[str]:
        """ Returns the names of all commands in this LMHCommander. """
        
        return list(map(lambda c:c.name, self.__commands))
    
    def has_command(self, name: str) -> bool:
        """ Checks if this LMHCommander contains a command with the given name.
        
        :param name: Name of command to check.
        """
        
        return name in self.keys()
    
    def __contains__(self, name: str) -> bool:
        """ Same as self.has_command(name).
        """
        
        return self.has_command(name)
    
    def get(self, name: str) -> Command:
        """ Gets the command with the given name or throws KeyError if it does
        not exist.
        
        :param name: Name of command to search for,
        """
        
        for k in self.__commands:
            if k.name == name:
                return k
        
        raise KeyError
    
    def __getitem__(self, name: str) -> Command:
        """ Same as self.get(name). """

        return self.get(name)
    
    def __safe_call(self, command: Command, *args: List[Any],
                    parsed_args: Optional[argparse.Namespace]=None) -> int:
        """ Internal function used to safely call a command.
        
        :param command: Command() instance to call.
        :param args: Arguments to forward to the call of the command.
        :param parsed_args: Parsed Arguments to forward to the call of this
        command.
        :return: An integer representing the return code.
        """
        
        # get the number of arguments required
        spec = inspect.getfullargspec(command.call)
        
        # num_args
        num_args = (len(spec.args) - 1)
        
        # has_parsed_args
        has_parsed_args = ('parsed_args' in spec.args) or ('parsed_args' in spec.kwonlyargs)
        
        if 'parsed_args' in spec.args:
            num_args -= 1
        
        # if we have the wrong number of arguments, exit
        if spec.varargs == None and len(args) != num_args:
            self.manager.logger.fatal(
                'Got the wrong number of arguments for ' +
                '%r (got %s, expected %s)' % (
                    'lmh %s' % command.name, len(args), num_args))
            return -4
        
        try:
            if has_parsed_args:
                ret = command(*args, parsed_args = parsed_args)
            else:
                ret = command(*args)
            if isinstance(ret, bool):
                return 0 if ret else 1
            elif isinstance(ret, int):
                return ret
            elif ret == None:
                return 0
            else:
                self.manager.logger.warn('Command %r ' % (command.name, ) +
                                         'did not return a valid return code')
                return 0
        except KeyboardInterrupt:
            self.manager.logger.error('Operation interrupted by user, exiting')
            return -1
        except LMHException as e:
            self.manager.logger.fatal('LMH has encountered a fatal '
                                      'error and has crashed. ')
            self.manager.logger.fatal('This error is likely caused by '
                                      'lmh itself. ')
            self.manager.logger.fatal(self.manager.logger\
                                      .get_exception_string(e))
            return -2
        except Exception as e:
            self.manager.logger.fatal('LMH has encountered a fatal error '
                                      'and has crashed. ')
            self.manager.logger.fatal('This error is likely caused by '
                                      'something outside of lmh. ')
            self.manager.logger.fatal(self.manager.logger\
                                      .get_exception_string(e))
            return -3

    def _build_argparse(self) -> argparse.ArgumentParser:
        """ Builds an argparse object representing this commander. """
        
        # Create the parser itself
        parser = argparse.ArgumentParser('lmh', description=self.__doc__)
        subparsers = parser.add_subparsers(dest='command', metavar='command')
        
        # iterate through the keys and check if we have a _build_argparse method
        for name in self.keys():
            c = self[name]
            try:
                c._build_argparse(subparsers)
            except NotImplementedError:
                subparsers.add_parser(name, help=self[name].__doc__,
                                      add_help=False)
        
        # add a version argument
        parser.add_argument('--version',
                            action='store_true',
                            help='show version message and exit. ' +
                                 'Alias for %r' % ('about',))
        
        # return the parser
        return parser

    def extract_arguments(self, *args: List[str])\
            -> Tuple[Optional[str], argparse.Namespace, List[str]]:
        """
        Extracts command to run and list of arguments from a command line.

        :param args: Arguments to parse.
        :return: A triple (command, parsed, unknown). command is the name of
        the command to be run or None (if a top-level action is performed).
        parsed is an arparse object representing the parsed arguments or None.
        unknown is a list of (unparsed) arguments.
        """
        
        # build the parser
        parser = self._build_argparse()
        
        # parse arguments
        try:
            (parsed, unknown) = parser.parse_known_args(args)
        except SystemExit:
            return (None, None, [])
        
        # extract the command
        command = parsed.command
        del parsed.command
        
        if parsed.version:
            return ('about', None, [])
        del parsed.version
        
        # If no arguments were given, print the help
        if command is None:
            parser.print_help()
            return (None, [], None)
        
        # return a triple
        return (command, parsed, unknown)
        
    def __call__(self, *args: List[str]) -> int:
        """ Runs this LMHCommander() on the given arguments.

        :param args: Arbitrary string arguments to pass to the commander.
        :return: An integer representing the return code of the command.
        """
        
        # extract the command
        (command, parsed, unknown) = self.extract_arguments(*args)
        
        if command is None:
            return 0
        else:
            return self.__safe_call(self[command], *unknown, parsed_args=parsed)
    
class CommanderWithoutManager(LMHException):
    """ Exception that is thrown when no LMHManager() is bound to an
    LMHCommander() instance. """
    
    def __init__(self):
        """ Creates a new CommanderWithoutManager() instance. """
        
        super(CommanderWithoutManager, self).__init__('No LMHManager() ' +
                                                      'is bound to this ' +
                                                      'LMHCommander() instance')

__all__ = ["LMHCommander", "CommanderWithoutManager"]
