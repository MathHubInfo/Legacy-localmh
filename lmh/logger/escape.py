from typing import Optional


class EscapeCode(str):
    """ An EscapeCode object represents an escapable color sequence. """
    
    def __new__(cls, value: Optional[str] = None, begin: Optional[str] = None,
                end: str = '\033[00m'):
        """ Creates a new EscapeCode object.
        
        :param value: Optional. String this object should represent.
        :param begin: Sequence that starts the escape code.
        :param end: Sequence that ends the escape code.
        :rtype: EscapeCode
        """
        
        if value == None:
            escaped_value = begin
        else:
            escaped_value = '%s%s%s' % (begin, value, end)
        
        return super(EscapeCode, cls).__new__(cls, escaped_value)


class Normal(EscapeCode):
    """ An Escape code that resets to normal text. """
    
    def __new__(cls, value: Optional[str] = None):
        """ Creates a new Normal() object.

        :param value: Optional. String value to wrap.
        :rtype: Normal
        """
        
        return super(Normal, cls).__new__(cls, value, begin = '\033[00m')


class Grey(EscapeCode):
    """ An Escape code that makes text Grey. """
    
    def __new__(cls, value: Optional[str] = None):
        """ Creates a new Grey() object.

        :param value: Optional. String value to wrap.
        :rtype: Grey
        """
        
        return super(Grey, cls).__new__(cls, value, begin = '\033[01;30m')

class Red(EscapeCode):
    """ An Escape code that makes text Red. """

    def __new__(cls, value: Optional[str] = None):
        """ Creates a new Red() object.

        :param value: Optional. String value to wrap.
        :rtype: Red
        """
        
        return super(Red, cls).__new__(cls, value, begin = '\033[01;31m')


class Green(EscapeCode):
    """ An Escape code that makes text Green. """

    def __new__(cls, value: Optional[str] = None):
        """ Creates a new Green() object.

        :param value: Optional. String value to wrap.
        :rtype: Green
        """
        
        return super(Green, cls).__new__(cls, value, begin = '\033[01;32m')


class Yellow(EscapeCode):
    """ An Escape code that makes text Yellow. """

    def __new__(cls, value: Optional[str] = None):
        """ Creates a new Yellow() object.

        :param value: Optional. String value to wrap.
        :rtype: Yellow
        """
        
        return super(Yellow, cls).__new__(cls, value, begin = '\033[01;33m')


class Blue(EscapeCode):
    """ An Escape code that makes text Blue. """

    def __new__(cls, value: Optional[str] = None):
        """ Creates a new Blue() object.

        :param value: Optional. String value to wrap.
        :rtype: Blue
        """
        
        return super(Blue, cls).__new__(cls, value, begin = '\033[01;34m')


class Magenta(EscapeCode):
    """ An Escape code that makes text Magenta. """

    def __new__(cls, value: Optional[str] = None):
        """ Creates a new Magenta() object.

        :param value: Optional. String value to wrap.
        :rtype: Magenta
        """

        return super(Magenta, cls).__new__(cls, value, begin = '\033[01;35m')


class Cyan(EscapeCode):
    """ An Escape code that makes text Cyan. """

    def __new__(cls, value: Optional[str] = None):
        """ Creates a new Cyan() object.

        :param value: Optional. String value to wrap.
        :rtype: Cyan
        """
        
        return super(Cyan, cls).__new__(cls, value, begin = '\033[01;36m')


class White(EscapeCode):
    """ An Escape code that makes text White. """

    def __new__(cls, value: Optional[str] = None):
        """ Creates a new White() object.

        :param value: Optional. String value to wrap.
        :rtype: White
        """
        
        return super(White, cls).__new__(cls, value, begin = '\033[01;37m')

__all__ = ["EscapeCode", "Normal", "Grey", "Red", "Green", "Yellow", "Blue",
           "Magenta", "Cyan", "White"]