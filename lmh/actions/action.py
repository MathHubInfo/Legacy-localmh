from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class Action(object):
    """
    An Action represents something that can be performed by lmh
    """
    
    def __init__(self, name, config):
        """
        Creates a new Action() instance. 
        
        Arguments: 
            name
                Name of this action
            config
                A list of LMHConfigSettingSpec() instances representing 
                configuration options needed by this action. 
        """
        
        self.name = name
        self.config = config
        
        self.manager = None
    
    def _register(self):
        """
        Protected Function that is called when this action is registered. 
        """
        pass
    
    def register(self, manager):
        """
        Registers this action with the given manager. 
        
        Arguments:
            manager
                LMHManager Instance that controls this action
        """
        
        self.manager = manager
        
        #  try updating the config
        if len(self.config) > 0:
            config_spec = self.manager.config.spec
            
            # add the config settings if they do not already exist
            for c in self.config:
                if not c.name in config_spec:
                    config_spec.add_config_setting(c)
                else:
                    self.manager.logger.warn('Action %r: Setting %r already exists in Manager() instance. ' % (self.name, c.name))
        
        self._register()
    
    def run(self, *args, **kwargs):
        """
        Runs this action. Should be implemented by the subclass. 
        
        Arguments: 
            *args, **kwargs
                Arbritrary arguments for this action
        Returns: 
            An Arbritrary object representing the result of the action
        """
        
        raise NotImplementedError
    def __call__(self, *args, **kwargs):
        """
        Same as self.run(*args, **kwargs)
        """
        return self.run(*args, **kwargs)

class AliasAction(Action):
    def __init__(self, name, alias_args, alias_kwargs,):
        super(AliasAction, self).__init__(name)