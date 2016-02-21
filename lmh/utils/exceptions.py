class LMHException(Exception):
    """
    Common base class for all exceptions used by LMH
    """
    
    def __init__(self, msg):
        """
        Creates a new LMHException() instance. 
        
        Arguments:
            msg
                Message describing this exception
        """
        
        super(LMHException, self).__init__(msg)

class MathHubException(LMHException):
    """
    Common base class for all Exceptions caused by the lmh.mathhub module
    """
    pass