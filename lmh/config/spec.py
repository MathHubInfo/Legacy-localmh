from lmh.utils.clsutils.caseclass import caseclass

class LMHConfigSpec(object):
    """
    Represents the specififcation for a list of LMH Config Values
    """
    
    def __init__(self, settings):
        """
        Creates a new LMHConfigSpec() instance. 
        
        Arguments:
            settings
                List of settings to use
        """
        
        self.settings = settings
    
    def keys(self):
        """
        Returns a list containing the names of all settings inside this 
        LMHConfigSpec() instance. 
        
        Returns:
            A list of strings
        """
        
        return list(map(lambda v:v.name, self.settings))
    
    def has(self, name):
        """
        Checks if this LMHConfigSpec() has a LMHConfigSettingSpec() key with the
        give name. 
        
        Arguments:
            name
                Name to check for
        Returns:
            A bool indicating it the key exists or not. 
        """
        
        try:
            self.get(name)
            return True
        except KeyError:
            return False
    
    def __contains__(self, name):
        """
        Same as self.has(name)
        """
        return self.has(name)
    
    def get(self, name):
        """
        Gets the LMHConfigSettingSpec() setting with the given name or throws
        KeyError. 
        
        Arguments:
            name
                Name of LMHConfigSettingSpec() instance to find
        Returns:
            LMHConfigSettingSpec() instance
        """
        
        matching = list(filter(lambda v:v.name==name, self.settings))
        
        if len(matching) >= 1:
            return matching[0]
        else:
            raise KeyError
    
    def __getitem__(self, name):
        """
        Same as self.get(name)
        """
        return self.get(name)

import json
from lmh.utils import fileio
class LMHFileConfigSpec(LMHConfigSpec):
    """
    Represents the specification of an LMHConfigSpec instance that is read
    from a json file on disk
    """
    
    def __init__(self, filename):
        """
        Creates a new LMHFileConfigSpec() instance
        
        Arguments:
            filename
                Filename of json file to read
        """
        
        super(LMHFileConfigSpec, self).__init__([
            LMHConfigSettingSpec(k, v["type"], v["default"], v["help"]) for (k, v) in json.loads(fileio.read_file(filename)).items()
        ])
        
@caseclass
class LMHConfigSettingSpec(object):
    """
    Represents the specification for a single lmh config settting. 
    """
    
    def __init__(self, name, tp, default, help_text=None):
        """
        Creates a new LMHConfigSettingSpec() instance. 
        
        Arguments:
            name
                Name of this setting. 
            tp
                The type of this setting. One of 'string', 'bool', 'int', 'int+'
            default
                The default value of this setting. 
            help_text
                Optional. A help string for this setting.
        """
        
        if not tp in ['string', 'bool', 'int', 'int+']:
            raise ValueError("Unsupported configuration type %r. Must be one of 'string', 'bool', 'int', 'int+'. " % tp)
        
        self.name = name
        self.tp = tp
        self.default = self.parse(default)
        self.help_text = help_text
    
    def parse(self, value):
        """
        Parses a value for this config setting into the proper type. 
        
        Arguments:
            value
                Value to parse. If None, return the default. 
        Returns:
            The parsed value for this setting. 
        """
        
        if value == None:
            return self.default
        
        elif self.tp == 'string':
            return str(value)
        
        elif self.tp == 'bool':
            if isinstance(value, bool):
                return value
            elif str(value).lower().strip() == 'true':
                return True
            else:
                return False
        
        elif self.tp == 'int':
            return int(value)
        
        elif self.tp == 'int+':
            if int(value) < 0:
                raise ValueError('Parameter for type %r must be >= 0' % 'int+')
            else:
                return int(value)
    def __call__(self, value):
        """
        Same as self.parse(value)
        """
        return self.parse(value)