from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class LogLevel(object):
    """
    Class used to represent different log levels for lmh
    """
    pass

@caseclass
class NoLogLevel(LogLevel):
    """
    Represents the None LogLevel for lmh - i. e. If only a message is written. 
    """
    pass

@caseclass
class InfoLogLevel(LogLevel):
    """
    Represents the Info LogLevel for lmh - i. e. If if an information is given
    """
    pass

@caseclass
class WarnLogLevel(LogLevel):
    """
    Represents the Warning LogLevel for lmh - i. e. if something is not entirely
    as intended
    """
    pass

@caseclass
class ErrorLogLevel(LogLevel):
    """
    Represents the Error LogLevel for lmh - i. e. if something went wrong and 
    lmh had to abort its current operation
    """
    pass

@caseclass
class FatalLogLevel(LogLevel):
    """
    Represents the Fatal LogLevel for lmh - i. e. if something went wrong and 
    lmh had to stop completly. Used only in case of uncaught exceptions. 
    """
    pass