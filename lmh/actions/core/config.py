from lmh.actions import action
from lmh.config.types import String, Bool, Int, PositiveInt
from lmh.logger import escape

class GetConfigAction(action.Action):
    """
    An action that gets a config setting
    """
    
    def __init__(self):
        """
        Creates a new GetConfigAction() instance
        """
        super(GetConfigAction, self).__init__('get-config')
    
    def run(self, name):
        """
        Runs this action
        
        Arguments: 
            name
                Name of config setting to get
        Returns: 
            The value of the config setting
        """
        
        return self.manager.config[name]


class GetConfigInfoAction(action.Action):
    """
    An action that returns info about a config setting
    """
    
    def __init__(self):
        """
        Creates a new GetConfigInfoAction() instance
        """
        super(GetConfigInfoAction, self).__init__('get-config-info')

    def color_type(self, tp):
        """
        Colorizes a type of a config setting
        
        Arguments:
            tp
                Type of config setting to color
        Returns:
            a colored string representing the tyüe
        """
        
        if tp is String():
            return escape.Yellow('string')
        elif tp is Bool():
            return escape.Green('bool')
        elif tp is Int():
            return escape.Blue('int')
        elif tp == PositiveInt():
            return escape.Blue('int+')
        else:
            return tp
    
    def get_short_info(self, name):
        """
        Gets info about a single command, including the default and current 
        value. 
        
        Arguments:
            name
                Name of config setting to get
        Returns:
            a string representing the information or None
        """
        
        try:
            value = repr(self.manager.config[name]) \
                if self.manager.config.is_set(name) else \
                escape.Grey(repr(self.manager.config[name]))
            spec = self.manager.config.get_spec(name)
        except KeyError:
            self.manager.logger.fatal('No such setting %r' % name)
            return None
        
        return '<%s> %s = %s' % (self.color_type(spec.tp), name, value)
    
    def get_info(self, name):
        """
        Gets info about a single command, including the default and current 
        value. 
        
        Arguments:
            name
                Name of config setting to get
        Returns:
            a string representing the information or None
        """
        
        try:
            value = repr(self.manager.config[name]) \
                if self.manager.config.is_set(name) else \
                escape.Grey(repr(self.manager.config[name]))
            spec = self.manager.config.get_spec(name)
        except KeyError:
            self.manager.logger.fatal('No such setting %r' % name)
            return None
        
        return '\n'.join([
            '<%s> %s' % (self.color_type(spec.tp), name), 
            spec.help_text or '', 
            'Current value: %s' % value,
            'Default value: %r' % spec.default
        ])
    
    def run(self, name = None):
        """
        Runs this action
        
        Arguments: 
            name
                Optional. Name of the config setting to get info about
        Returns: 
            Information about the config setting of None
        """
        
        if name == None:
            return '\n'.join(map(self.get_short_info, sorted(self.manager.config.keys())))
        else:
            return self.get_info(name)
        
class SetConfigAction(action.Action):
    """
    An action that gets a config setting
    """
    
    def __init__(self):
        """
        Creates a new SetConfigAction() instance
        """
        super(SetConfigAction, self).__init__('set-config')
    
    def run(self, name, value):
        """
        Runs this action
        
        Arguments: 
            name
                Name of config setting to set
            value
                Value to set config setting to
        """
        
        self.manager.config[name] = value

class ResetConfigAction(action.Action):
    """
    An action that resets a config setting
    """
    
    def __init__(self):
        """
        Creates a new ResetConfigAction() instance
        """
        super(ResetConfigAction, self).__init__('reset-config')
    
    def run(self, name):
        """
        Runs this action
        
        Arguments: 
            name
                Name of config setting to reset
        """
        
        del self.manager.config[name]