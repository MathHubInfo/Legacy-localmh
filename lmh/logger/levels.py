from deps.PythonCaseClass.case_class import AbstractCaseClass

class LogLevel(AbstractCaseClass):
    """ Class used to represent different log levels for lmh. """
    def __init__(self):
        super(LogLevel, self).__init__()


class NoLogLevel(LogLevel):
    """ Represents the None LogLevel for lmh - i.e. If only a message is written. """
    pass


class InfoLogLevel(LogLevel):
    """ Represents the Info LogLevel for lmh - i.e. If if an information is given. """

    pass


class WarnLogLevel(LogLevel):
    """ Represents the Warning LogLevel for lmh - i.e. if something is not entirely as intended. """

    pass


class ErrorLogLevel(LogLevel):
    """ Represents the Error LogLevel for lmh - i.e. if something went wrong and lmh had to abort its current
    operation. """
    pass


class FatalLogLevel(LogLevel):
    """ Represents the Fatal LogLevel for lmh - i.e. if something went wrong and lmh had to stop completly. Used only
    in case of uncaught exceptions.
    """
    pass