from typing import Any, Optional, List
import json

from deps.PythonCaseClass.case_class import AbstractCaseClass, CaseClass
from lmh.utils.fileio import FileIO

from lmh.config.types import ConfigSettingType


class LMHConfigSettingSpec(CaseClass):
    """ Represents the specification for a single lmh config setting. """

    def __init__(self, name: str, tp: ConfigSettingType, default: Any,
                 help_text: Optional[str]=None):
        """ Creates a new LMHConfigSettingSpec() instance.

        :param name: Name of this setting.
        :param tp: The type of this setting.
        :param default: The default value for this setting.
        :param help_text: Optional. A help string for this setting.
        """

        if isinstance(tp, str):
            tp = ConfigSettingType.from_string(tp)

        self.__name = name  # type: str
        self.__tp = tp  # type: ConfigSettingType
        self.__default = self.check(default)
        self.__help_text = help_text

    @property
    def name(self) -> str:
        """ Gets the name of this LMH Config Setting. """

        return self.__name

    @property
    def tp(self) -> ConfigSettingType:
        """ Gets the type of this LMH Config Setting. """

        return self.__tp

    @property
    def default(self) -> Any:
        """ Returns the default of this LMH Config Setting. """

        return self.__default

    @property
    def help_text(self) -> str:
        """ Returns the help text of this LMH Config Setting. """

        return self.__help_text

    def parse(self, value: str) -> Any:
        """ Called to parse user input into a value of this setting.

        :param value: Value to parse.
        """

        return self.tp.check(value)

    def __call__(self, value: str) -> Any:
        """ Same as self.parse(value). """

        return self.parse(value)

    def check(self, value: Any) -> Any:
        """ Called to check that a stored value of this setting is actually of
        the right type. Should clean up value. Should raise ValueError() or
        TypeError() it it is not of the expected type.

        :param value: Value to check.
        """

        return self.tp.check(value)


class LMHConfigSpec(AbstractCaseClass):
    """ Represents the specififcation for a list of LMH Config Values. """
    
    def __init__(self, settings: List[LMHConfigSettingSpec]):
        """ Creates a new LMHConfigSpec() instance.

        :param settings: List of settings to use.
        """
        
        self.__settings = list(settings)  # type: List[LMHConfigSettingSpec]
        
        # check that we have each key only once
        keys = self.keys()
        if len(keys) != len(list(set(keys))):
            raise ValueError('Duplocate key inside settings parameters')

    @property
    def settings(self) -> List[LMHConfigSettingSpec]:
        """ Returns the list of settings are associated with this
        LMHConfiSettingSpec. """

        return self.__settings
    
    def add_config_setting(self, setting: LMHConfigSettingSpec) -> None:
        """
        Adds an LMHConfigSettingSpec() instance to this LMHConfigSpec() or
        raises ValueError() if it already exists.

        :param setting: Setting to add.
        """
        
        if not isinstance(setting, LMHConfigSettingSpec):
            raise TypeError('setting has to be an instance of ' +
                            'LMHConfigSettingSpec()')
        
        if setting.name in self:
            raise ValueError('A setting named %r is already inside this ' +
                             'LMHConfigSpec()')
        
        self.settings.append(setting)
    
    def keys(self) -> List[str]:
        """ Returns a list containing the names of all settings inside this
        LMHConfigSpec() instance. """
        
        return list(map(lambda v:v.name, self.settings))
    
    def has(self, name: str) -> bool:
        """ Checks if this LMHConfigSpec() has a LMHConfigSettingSpec() key
        with the give name.

        :param name: Name to check for.
        """
        
        try:
            self.get(name)
            return True
        except KeyError:
            return False
    
    def __contains__(self, name: str) -> bool:
        """ Same as self.has(name). """

        return self.has(name)
    
    def get(self, name: str) -> LMHConfigSettingSpec:
        """ Gets the LMHConfigSettingSpec() setting with the given name or
        throws KeyError.

        :param name: Name of LMHConfigSettingSpec() instance to find.
        """

        for v in self.settings:
            if v.name == name:
                return v

        raise KeyError
    
    def __getitem__(self, name: str) -> LMHConfigSettingSpec:
        """ Same as self.get(name). """

        return self.get(name)


class LMHFileConfigSpec(LMHConfigSpec):
    """ Represents the specification of an LMHConfigSpec instance that is read
    from a json file on disk. """
    
    def __init__(self, filename: str):
        """ Creates a new LMHFileConfigSpec() instance.
        
        :param filename: Filename of json file to read.
        """
        
        super(LMHFileConfigSpec, self).__init__([
            LMHConfigSettingSpec(k, ConfigSettingType.from_string(v["type"]),
                                 v["default"], v["help"])
            for (k, v) in json.loads(FileIO.read_file(filename)).items()
        ])

__all__ = ["LMHConfigSettingSpec", "LMHConfigSpec", "LMHConfigSettingSpec"]
