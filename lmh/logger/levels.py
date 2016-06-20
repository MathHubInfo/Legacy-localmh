from deps.PythonCaseClass.case_class import AbstractCaseClass


class LogLevel(AbstractCaseClass):
    """ Class used to represent different log levels for lmh. """

    pass


class NoLogLevel(LogLevel):
    """ Represents the lowest Log Level for lmh - i.e. if only a message is
    written. """

    pass


class InfoLogLevel(LogLevel):
    """ Represents the Info LogLevel for lmh - i.e. an informational
    message. """

    pass


class WarnLogLevel(LogLevel):
    """ Represents the Warning LogLevel for lmh - i.e. if something is not
    entirely as intended. """

    pass


class ErrorLogLevel(LogLevel):
    """ Represents the Error LogLevel for lmh - i.e. if something went wrong
    and lmh had to abort its current operation. """

    pass


class FatalLogLevel(LogLevel):
    """ Represents the Fatal LogLevel for lmh - i.e. if something went wrong
    and lmh had to stop completly. Used only in case of uncaught exceptions.
    """

    pass

__all__ = ["LogLevel", "NoLogLevel", "InfoLogLevel", "WarnLogLevel",
           "ErrorLogLevel", "FatalLogLevel"]