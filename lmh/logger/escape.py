class EscapeCode(str):
    """
    An EscapeCode object represents an escapable color sequence. 
    """
    
    def __new__(cls, value = None, begin = None, end = '\033[00m'):
        """
        Creates a new EscapeCode object. 
        
        Arguments:
            *value
                Optional. Strings this object should represent
            begin
                Sequence that starts the escape code
            end
                Sequence that ends the escape code
        """
        
        if value == None:
            escaped_value = begin
        else:
            escaped_value = '%s%s%s' % (begin, value, end)
        
        return super(EscapeCode, cls).__new__(cls, escaped_value)

class Normal(EscapeCode):
    """
    An Escape code that resets to normal text
    """
    
    def __new__(cls, value = None):
        """
        Creates a new Normal() object. 
        
        Arguments: 
            value
                Optional. String value to wrap. 
        Returns:
            A new Normal() instance
        """
        
        return super(Normal, cls).__new__(cls, value, begin = '\033[00m')

class Grey(EscapeCode):
    """
    An Escape code that makes text Grey. 
    """
    
    def __new__(cls, value = None):
        """
        Creates a new Grey() object. 
        
        Arguments: 
            value
                Optional. String value to wrap. 
        Returns:
            A new Grey() instance
        """
        
        return super(Grey, cls).__new__(cls, value, begin = '\033[01;30m')

class Red(EscapeCode):
    """
    An Escape code that makes text Red. 
    """
    
    def __new__(cls, value = None):
        """
        Creates a new Red() object. 
        
        Arguments: 
            value
                Optional. String value to wrap. 
        Returns:
            A new Red() instance
        """
        
        return super(Red, cls).__new__(cls, value, begin = '\033[01;31m')

class Green(EscapeCode):
    """
    An Escape code that makes text Green. 
    """
    
    def __new__(cls, value = None):
        """
        Creates a new Green() object. 
        
        Arguments: 
            value
                Optional. String value to wrap. 
        Returns:
            A new Green() instance
        """
        
        return super(Green, cls).__new__(cls, value, begin = '\033[01;32m')

class Yellow(EscapeCode):
    """
    An Escape code that makes text Yellow. 
    """
    
    def __new__(cls, value = None):
        """
        Creates a new Yellow() object. 
        
        Arguments: 
            value
                Optional. String value to wrap. 
        Returns:
            A new Yellow() instance
        """
        
        return super(Yellow, cls).__new__(cls, value, begin = '\033[01;33m')

class Blue(EscapeCode):
    """
    An Escape code that makes text Blue. 
    """
    
    def __new__(cls, value = None):
        """
        Creates a new Blue() object. 
        
        Arguments: 
            value
                Optional. String value to wrap. 
        Returns:
            A new Blue() instance
        """
        
        return super(Blue, cls).__new__(cls, value, begin = '\033[01;34m')

class Magenta(EscapeCode):
    """
    An Escape code that makes text Magenta. 
    """
    
    def __new__(cls, value = None):
        """
        Creates a new Magenta() object. 
        
        Arguments: 
            value
                Optional. String value to wrap. 
        Returns:
            A new Magenta() instance
        """
        
        return super(Magenta, cls).__new__(cls, value, begin = '\033[01;35m')

class Cyan(EscapeCode):
    """
    An Escape code that makes text Cyan. 
    """
    
    def __new__(cls, value = None):
        """
        Creates a new Cyan() object. 
        
        Arguments: 
            value
                Optional. String value to wrap. 
        Returns:
            A new Cyan() instance
        """
        
        return super(Cyan, cls).__new__(cls, value, begin = '\033[01;36m')

class White(EscapeCode):
    """
    An Escape code that makes text White. 
    """
    
    def __new__(cls, value = None):
        """
        Creates a new White() object. 
        
        Arguments: 
            value
                Optional. String value to wrap. 
        Returns:
            A new White() instance
        """
        
        return super(White, cls).__new__(cls, value, begin = '\033[01;37m')