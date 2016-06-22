import json
import os.path

from typing import Optional, Any, Dict, List

from lmh.config.spec import LMHConfigSpec, LMHConfigSettingSpec

from lmh.utils.fileio import FileIO
from deps.PythonCaseClass.case_class import AbstractCaseClass


class LMHConfig(AbstractCaseClass):
    """ Represents an LMH Configuration that can be read and written by lmh. """
    
    def __init__(self, spec: LMHConfigSpec):
        """ Creates a new LMHConfig instance.
        
        :param spec: LMHConfigSpec() instance representing the given
        configuration settings.
        """
        
        self.__spec = spec  # type: LMHConfigSpec
        self.__dict = None  # type: Optional[Dict[str, Any]]

    @property
    def spec(self) -> LMHConfigSpec:
        """ Gets the LMHConfigSpec instance represeting the settings. """

        return self.__spec

    def _read_dict(self) -> Dict[str, Any]:
        """ Protected function used to read the configuration dictionary from
        storage. Should be overridden by subclass.
        
        :return: A dict object that represents the directory on disk.
        """
        
        raise NotImplementedError
    
    def _write_dict(self, d: Dict[str, Any]) -> bool:
        """ Protected function used to write the configuration dictionary to
        storage. Should be overridden by subclass.
        
        :param d: Current state of the content directory that should be written
        to disk.
        :return: A boolean indicating if the write process was successful.
        """
        
        raise NotImplementedError
    
    def __update_dict(self, force: bool = False) -> None:
        """ Protected function used to update the cached version of the
        settings.
        
        :param force: Optional. If set to True, always reloads the dictionary
        from disk.
        """

        if (self.__dict is None) or force:
            self.__dict = self._read_dict()
    
    def get(self, name: str) -> Any:
        """ Gets the value of a configuation setting or raises KeyError if it does
        not exist.

        :param name: The name of the configuration setting to get.
        :return: the current value of the configuration setting.
        """
        
        if not self.has(name):
            raise KeyError
        
        self.__update_dict()

        #get the correct setting
        setting = self.spec[name]

        # if it is set, simply cleanup the value
        if self.is_set(name):
            return setting.check(self.__dict[name])

        # else get the default
        else:
            return setting.default
    
    def __getitem__(self, name: str) -> Any:
        """ Same as self.get(name).  """

        return self.get(name)
    
    def has(self, name: str) -> bool:
        """ Checks if this LMHConfig() instance has the configuration setting
        with the given name.

        :param name: The name of the configuration setting to check.
        :return: a boolean indicating if the setting is supported.
        """
        
        return name in self.spec
    
    def __contains__(self, name: str) -> bool:
        """ Same as self.has(name). """

        return self.has(name)
    
    def keys(self) -> List[str]:
        """ Returns a list containing the names of all settings inside this
        LMHConfig() instance. """
        
        return self.spec.keys()
    
    def get_spec(self, name: str) -> LMHConfigSettingSpec:
        """ Returns the LMHConfigSettingSpec() instance for the key with the
        given name or raises KeyError.
        
        :param name: Name of LMHConfigSettingSpec() instance to get.
        """
        
        return self.spec[name]
    
    def is_set(self, name: str) -> bool:
        """ Checks if this LMHConfig() instance has the given configuration
        setting set.

        :param name: Name of configuration setting to check.
        """
        
        if not self.has(name):
            raise KeyError
        
        self.__update_dict()
        
        return name in self.__dict.keys()
    
    def set(self, name: str, value: Any) -> bool:
        """ Sets the value of a configuration setting to the given value or
        raises KeyError if it does not exist.
        
        :param name: Name of configuration setting to set.
        :param value: Value to set it to.

        :return: A boolean indicating if the change was successful or not.
        """
        
        if not self.has(name):
            raise KeyError
        
        self.__update_dict(force = True)

        setting = self.spec[name]

        try:
            self.__dict[name] = setting.check(value)

            return self._write_dict(self.__dict)
        except KeyError:
            pass
        except ValueError:
            pass

        self.__dict[name] = setting.parse(value)

        return self._write_dict(self.__dict)

    
    def __setitem__(self, key: str, value: Any) -> bool:
        """ Same as self.set(key, value).  """

        return self.set(key, value)
    
    def reset(self, name: str) -> bool:
        """ Resets a configuration setting to its default value or throws
        KeyError if it does not exist.

        :param name: Name of configuration setting to reset.
        :return: A boolean indicating if the change was successful or not.
        """
        
        if not self.has(name):
            raise KeyError
        
        self.__update_dict(force = True)
        
        try:
            del self.__dict[name]
        except KeyError:
            pass
        
        return self._write_dict(self.__dict)
    
    def __delitem__(self, name: str) -> bool:
        """ Same as self.reset(key, value).  """

        return self.reset(name)


class LMHJSONFileConfig(LMHConfig):
    """ Represents an LMHConfig instance that can read from a JSON file. """
    
    def __init__(self, spec: LMHConfigSpec, filename: str):
        """ Creates a new LMHJSONFileConfig() instance.
        
        :param LMHConfigSpec() instance representing the given configuration
        settings.
        :param filename: Filename of file to read.
        """

        super(LMHJSONFileConfig, self).__init__(spec)
        
        self.__filename = filename  # type: str
    
    def _read_dict(self) -> Dict[str, Any]:
        """ Protected function used to read the configuration dictionary from
        storage.
        
        :return: A dict object that represents the directory on disk.
        """
        
        if os.path.isfile(self.__filename):
            return json.loads(FileIO.read_file(self.__filename))
        else:
            return {}
    
    def _write_dict(self, d: Dict[str, Any]) -> bool:
        """ Protected function used to write the configuration dictionary to
        storage.
        
        :param d: Current state of the content directory that should be written
        to disk.
        :return: A boolean indicating if the write process was successful.
        """

        try:
            d_str = json.dumps(d, sort_keys=True, indent=4)
        except:
            return False
        
        # if there is nothing to write to the file, delete it. 
        if d_str == r'{}':
            try:
                os.remove(self.__filename)
            except FileNotFoundError:
                pass

            return True
        
        return FileIO.write_file(self.__filename, d_str)


class LMHInMemoryConfig(LMHConfig):
    """ Represents an in-memory configuration instance.
    """
    
    def __init__(self, spec):
        """ Creates a new LMHInMemoryConfig() instance.
        
        :param spec: LMHConfigSpec() instance representing the given
        configuration settings.
        """

        super(LMHInMemoryConfig, self).__init__(spec)
        
        self.__cache = {}  # type: Dict[str, Any]
    
    def _read_dict(self) -> Dict[str, Any]:
        """ Protected function used to read the configuration dictionary from
        storage. """
        
        return self.__cache
    
    def _write_dict(self, d: Dict[str, Any]) -> bool:
        """ Protected function used to write the configuration dictionary to
        storage.
        
        :param d: Current state of the content directory that should be written
        to storage.
        """
        
        self.__cache = d

        return True

__all__ = ["LMHConfig", "LMHJSONFileConfig", "LMHInMemoryConfig"]