from typing import List, Any, Optional

from lmh.logger import escape
from lmh.logger.levels import LogLevel, NoLogLevel, InfoLogLevel, \
    WarnLogLevel, ErrorLogLevel, FatalLogLevel

import sys
import traceback


class Logger(object):
    """ Represents a logger used by lmh. Should be subclassed. """
    
    def __init__(self, name: str):
        """ Creates a new logger instance.

        :param name: Name of this logger.
        """

        self.__name = name  # type: str

    @property
    def name(self) -> str:
        """ Gets the name of this logger. """

        return self.__name
    
    def _log(self, *message: List[Any], newline: bool = True,
             level: LogLevel = NoLogLevel()) -> None:
        """ Protected method used to log output. Should be overridden by subclass.

        :param message: List of objects that should be written to the log.
        :param newline: Should a newline be added at the end of the log message?
        Defaults to true.
        :param level: LogLevel() object representing the logLevel of this
        message. Defaults to levels.NoLogLevel().
        """

        raise NotImplementedError
    
    def log(self, *message: List[Any], newline: bool = True,
            flush: bool = False, level: LogLevel = NoLogLevel())\
            -> None:
        """ Writes a message to the log.

        :param message: List of objects that should be written to the log.
        :param newline: Should a newline be added at the end of the log message?
         Defaults to true.
        :param flush: Should output be flushed automatically? If set to True
        automatically calls self.flush().
        :param level: LogLevel() object representing the logLevel of this
        message. Defaults to levels.NoLogLevel().
        """
        
        self._log(*message, newline = newline, level = level)
        
        if flush:
            self.flush()
    
    def flush(self) -> None:
        """
        Flushes output of this logger. Should be overridden by subclass. 
        """

        raise NotImplementedError
    
    def info(self, *message: List[Any], newline: bool = True,
             flush: bool = False) -> None:
        """ Writes a message to the log with the level InfoLogLevel().
        
        :param message: List of objects that should be written to the log.
        :param newline: Should a newline be added at the end of the log
        message? Defaults to true.
        :param flush: Should output be flushed automatically? If set to True
        automatically calls self.flush().
        """
        
        return self.log(*message, newline=newline, flush=flush,
                        level=InfoLogLevel())
    
    def warn(self, *message: List[Any], newline: bool = True,
             flush: bool = False) -> None:
        """ Writes a message to the log with the WarnLogLevel().
        
        :param message: List of objects that should be written to the log.
        :param newline: Should a newline be added at the end of the log message?
         Defaults to true.
        :param flush: Should output be flushed automatically? If set to True
        automatically calls self.flush().
        """
        
        return self.log(*message, newline=newline, flush=flush,
                        level=WarnLogLevel())
    
    def error(self, *message: List[Any], newline: bool = True,
              flush: bool = False) -> None:
        """ Writes a message to the log with the ErrorLogLevel().

        :param message: List of objects that should be written to the log.
        :param newline: Should a newline be added at the end of the log message?
         Defaults to true.
        :param flush: Should output be flushed automatically? If set to True
        automatically calls self.flush().
        """
        
        return self.log(*message, newline=newline, flush=flush,
                        level=ErrorLogLevel())
    
    def fatal(self, *message: List[Any], newline: bool = True,
              flush: bool = False) -> None:
        """ Writes a message to the log with the FatalLogLevel().

        :param message: List of objects that should be written to the log.
        :param newline: Should a newline be added at the end of the log message?
         Defaults to true.
        :param flush: Should output be flushed automatically? If set to True
        automatically calls self.flush().
        """
        
        return self.log(*message, newline=newline, flush=flush,
                        level=FatalLogLevel())
    
    @staticmethod
    def get_exception_string(exception: Exception) -> str:
        """ Returns a string formatting an exception.

        :param exception: Exception to format.
        :return: A string representing the exception and its traceback.
        """
        
        return ''.join(traceback.format_exception(exception.__class__,
                                                  exception,
                                                  exception.__traceback__))
        

class StandardLogger(Logger):
    """ Represents a Logger that logs to STDOUT / STDERR. """
    
    def __init__(self):
        """ Creates a new logger StandardLogger() instance. """

        super(StandardLogger, self).__init__('standard')

        self._lastlog = None  # type: Optional[str]
    
    def __write_std(self, msg: str) -> None:
        """ Private function used to write to stdout.
        
        :param msg: String to write to stdout.
        """
        
        if self._lastlog == 'stderr':
            sys.stderr.flush()
        
        sys.stdout.write(msg)
        
        self._lastlog = 'stdout'
    
    def __write_err(self, msg: str) -> None:
        """ Private function used to write to stderr.
        
        :param msg: String to write to stdout.
        """
        
        if self._lastlog == 'stdout':
            sys.stdout.flush()
        
        sys.stderr.write(msg)
        
        self._lastlog = 'stderr'
    
    def _log(self, *message : List[Any], newline : bool = True,
             level: LogLevel = NoLogLevel()) -> None:
        """ Protected method used to log output. Should be overridden by
        subclass.

        :param message: List of objects that should be written to the log
        :param newline: Should a newline be added at the end of the log message?
         Defaults to true.
         :param level: LogLevel() object representing the logLevel of this
         message. Defaults to NoLogLevel()
        """
        
        msg = ' '.join(list(map(str, message)))
        
        if newline:
            msg += '\n'
        
        # nothing special, just print
        if level == NoLogLevel():
            self.__write_std(msg)
        
        # Info ==> STDOUT
        elif level == InfoLogLevel():
            self.__write_std('[%s] %s' % (escape.Green('info'), msg))
        
        # Warn + Error + Fatal ==> STDERR
        elif level == WarnLogLevel():
            self.__write_err('[%s] %s' % (escape.Yellow('warn'), msg))
        elif level == ErrorLogLevel():
            self.__write_err('[%s] %s' % (escape.Red('error'), msg))
        elif level == FatalLogLevel():
            self.__write_err('[%s] %s' % (escape.Magenta('fatal'), msg))
    
    def flush(self) -> None:
        """ Flushes output of this logger. Should be overridden by subclass. """
        
        sys.stdout.flush()
        sys.stderr.flush()