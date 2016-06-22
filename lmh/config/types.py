from typing import Any

from deps.PythonCaseClass.case_class import AbstractCaseClass


class ConfigSettingType(AbstractCaseClass):
    """ Represents a set of ConfigSetting types available. """

    def __init__(self):
        """Creates a new ConfigSettingType() instance. """
        pass

    def check(self, value: Any) -> Any:
        """ Called to check that a stored value of this type is actually of this
        type. Should clean up value. Should raise ValueError() or TypeError() if
        it is not of the expected type.

        :param value: Value to check.
        """

        raise NotImplementedError

    def parse(self, value: str) -> Any:
        """ Called to parse user input into a value of this type.

        :param value: Value to parse.
        """

        raise NotImplementedError


    @staticmethod
    def from_string(s):
        """ Returns the ConfigSettingType belonging to the given string. May
        trust the input it gets.

        :param s: String to turn into an ConfigSettingType.
        :rtype: ConfigSettingType
        """

        if s == 'string':
            return String()
        elif s == 'bool':
            return Bool()
        elif s == 'int':
            return Int()
        elif s == 'int+':
            return PositiveInt()
        else:
            raise ValueError('Unknown ConfigSettingType %r. ' % (s, ))


class String(ConfigSettingType):
    """ Represents a string value. """

    def check(self, value: Any) -> str:
        """ Called to check that a stored value of this type is actually of this
        type. Should clean up value. Should raise ValueError() or TypeError() if
        it is not of the expected type.

        :param value: Value to check.
        """

        if not isinstance(value, str):
            raise TypeError("value should be a string. ")

        return str(value)

    def parse(self, value: str) -> str:
        """ Called to parse user input into a value of this type.

        :param value: Value to parse.
        """

        return str(value)


class Bool(ConfigSettingType):
    """ Represents a bool type. """

    def check(self, value: Any) -> bool:
        """ Called to check that a stored value of this type is actually of this
        type. Should clean up value. Should raise ValueError() or TypeError() if
        it is not of the expected type.

        :param value: Value to check.
        """

        if not isinstance(value, bool):
            raise TypeError("value should be a bool. ")

        return bool(value)

    def parse(self, value: str) -> str:
        """ Called to parse user input into a value of this type.

        :param value: Value to parse.
        """

        s = value.lower().strip()

        if s == 'true':
            return True
        elif s == 'false':
            return False
        elif len(s) > 0:
            if s[0] == 'y':
                return True
            elif s[0] == 't':
                return True
            else:
                return False


class Int(ConfigSettingType):
    def check(self, value: Any) -> int:
        """ Called to check that a stored value of this type is actually of this
        type. Should clean up value. Should raise ValueError() or TypeError() if
        it is not of the expected type.

        :param value: Value to check.
        """

        if not isinstance(value, int):
            raise TypeError("value should be an int. ")

        return int(value)

    def parse(self, value: str) -> str:
        """ Called to parse user input into a value of this type.

        :param value: Value to parse.
        """

        return int(value)


class PositiveInt(Int):
    def check(self, value: Any) -> int:
        """ Called to check that a stored value of this type is actually of this
        type. Should clean up value. Should raise ValueError() or TypeError() if
        it is not of the expected type.

        :param value: Value to check.
        """

        v = super(PositiveInt, self).check(value)

        if v < 0:
            raise ValueError("value should be a positive int. ")

        return v

    def parse(self, value: str) -> str:
        """ Called to parse user input into a value of this type.

        :param value: Value to parse.
        """

        return int(value)

__all__ = ["ConfigSettingType", "String", "Bool", "Int", "PositiveInt"]