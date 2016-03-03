class LMHConfig(object):
    """
    Represents an LMH Configuration that can be read and written by lmh
    """
    
    def __init__(self, spec):
        """
        Creates a new LMHConfig instance. 
        
        Arguments:
            spec
                LMHConfigSpec() instance representing the given configuration
                settings
        """
        
        self.spec = spec
        self.__dict = None
    
    def _read_dict(self):
        """
        Protected function used to read the configuration dictionary from 
        storage. 
        Should be overriden by subclass. 
        
        Returns:
            A dict object that represents the directory on disk. 
        """
        
        raise NotImplementedError
    
    def _write_dict(self, d):
        """
        Protected function used to write the configuration dictionary to 
        storage. Should be overriden by subclass. 
        
        Arguments:
            d
                Current state of the content directory that should be written 
                to disk. 
        Returns: 
            A boolean indicating if the write process was successfull
        """
        
        raise NotImplementedError
    
    def __update_dict(self, force = False):
        """
        Private function the cached version of the settings. 
        
        Arguments:
            force
                Optional. If set to True, always reloads the dictionary from 
                disk. 
        """
        if (self.__dict == None) or force:
            self.__dict = self._read_dict()
    
    def get(self, name):
        """
        Gets the value of a configuation setting or raises KeyError if it does 
        not exist. 
        
        Arguments:
            name
                The name of the configuration setting to get
        Returns: 
            the current value of the configuration setting
        """
        
        if not self.has(name):
            raise KeyError
        
        self.__update_dict()
        
        return self.spec[name](self.__dict[name] if self.is_set(name) else None)
    
    def __getitem__(self, name):
        """
        Same as self.get(name)
        """
        return self.get(name)
    
    def has(self, name):
        """
        Checks if this LMHConfig() instance has the configuration setting with
        the given name. 
        
        Arguments:
            name
                The name of the configuration setting to check
        Returns: 
            a boolean indicating if the setting is supported
        """
        
        return name in self.spec
    
    def __contains__(self, name):
        """
        Same as self.has(name)
        """
        return self.has(name)
    
    def keys(self):
        """
        Returns a list containing the names of all settings inside this 
        LMHConfig() instance. 
        
        Returns:
            A list of strings
        """
        
        return self.spec.keys()
    
    def get_spec(self, name):
        """
        Returns the LMHConfigSettingSpec() instance for the key with the given
        name or raises KeyError. 
        
        Arguments:
            name
                Name of LMHConfigSettingSpec() instance to get
        Returns:
            An LMHConfigSettingSpec() instance
        """
        
        return self.spec[name]
    
    def is_set(self, name):
        """
        Checks if this LMHConfig() instance has the given configuration setting
        set. 
        
        Arguments:
            name
                Name of configuration setting to check
        Returns:
            A boolean indicating if the setting is set. 
        """
        
        if not self.has(name):
            raise KeyError
        
        self.__update_dict()
        
        return name in self.__dict.keys()
    
    def set(self, name, value):
        """
        Sets the value of a configuation setting to the given value or raises
        KeyError if it does not exist. 
        
        Arguments:
            name
                Name of configuration setting to set
            value
                Value to set it to
        Returns:
            A boolean indicating if the change was successfull or not
        """
        
        if not self.has(name):
            raise KeyError
        
        self.__update_dict(force = True)
        
        self.__dict[name] = self.spec[name].serialise(value)
        
        return self._write_dict(self.__dict)
    
    def __setitem__(self, key, value):
        """
        Same as self.set(key, value)
        """
        return self.set(key, value)
    
    def reset(self, name):
        """
        Resets a configuration setting to its default value or throws KeyError
        if it does not exist. 
        
        Arguments:
            name
                Name of configuration setting to reset
        Returns:
            A boolean indicating if the change was successfull or not
        """
        
        if not self.has(name):
            raise KeyError
        
        self.__update_dict(force = True)
        
        try:
            del self.__dict[name]
        except KeyError:
            pass
        
        return self._write_dict(self.__dict)
    
    def __delitem__(self, name):
        """
        Same as self.reset(key, value)
        """
        return self.reset(name)

import os.path
import json
from lmh.utils import fileio
from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class LMHJSONFileConfig(LMHConfig):
    """
    Represents an LMHConfig instance that can read from a file
    """
    
    def __init__(self, spec, filename):
        """
        Creates a new LMHReadOnlyConfig() instance. 
        
        Arguments:
            spec
                LMHConfigSpec() instance representing the given configuration
                settings
            filename
                Filename of file to read
            
        """
        super(LMHJSONFileConfig, self).__init__(spec)
        
        self.__filename = filename
    
    def _read_dict(self):
        """
        Protected function used to read the configuration dictionary from 
        storage. 
        Should be overriden by subclass. 
        
        Returns:
            A dict object that represents the directory on disk. 
        """
        
        if os.path.isfile(self.__filename):
            return json.loads(fileio.read_file(self.__filename))
        else:
            return {}
    
    def _write_dict(self, d):
        """
        Protected function used to write the configuration dictionary to 
        storage. Should be overriden by subclass. 
        
        Arguments:
            d
                Current state of the content directory that should be written 
                to disk. 
        Returns: 
            A boolean indicating if the write process was successfull
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
        
        return fileio.write_file(self.__filename, d_str)

from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class LMHReadOnlyConfig(LMHConfig):
    """
    Represents a read-only LMH Config instance
    """
    
    def __init__(self, spec):
        """
        Creates a new LMHReadOnlyConfig() instance. 
        
        Arguments:
            spec
                LMHConfigSpec() instance representing the given configuration
                settings
        """
        super(LMHFileConfig, self).__init__(spec)
        
        self.__cache = {}
    
    def _read_dict(self):
        """
        Protected function used to read the configuration dictionary from 
        storage. 
        Should be overriden by subclass. 
        
        Returns:
            A dict object that represents the directory on disk. 
        """
        
        return self.__cache
    
    def _write_dict(self, d):
        """
        Protected function used to write the configuration dictionary to 
        storage. Should be overriden by subclass. 
        
        Arguments:
            d
                Current state of the content directory that should be written 
                to disk. 
        Returns: 
            A boolean indicating if the write process was successfull
        """
        
        self.__cache = d
        return d