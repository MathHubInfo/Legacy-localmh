from lmh.actions import action
import os

class LocateAction(action.Action):
    """
    An action that can locate core files within lmh
    """
    
    def __init__(self, systems_dir = '..', config_dir = 'data/config', spec_dir = 'data/spec'):
        """
        Creates a new LocateAction() instance. 
        
        Arguments:
            systems_dir
                Direcory to find all systems in. Defaults to '..'. 
            config_dir
                Directory to find user configuration in. Defaults to 
                'data/config'. 
            spec_dir
                Directory to find spec files in. Defaults to 'data/spec'. 
        """
        
        # Setup all the directories
        self._base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',  '..',  '..'))
        self._systems = os.path.abspath(os.path.join(self._base, systems_dir))
        self._config = os.path.abspath(os.path.join(self._base, config_dir))
        self._spec = os.path.abspath(os.path.join(self._base, spec_dir))
        
        super(LocateAction, self).__init__('locate')
    
    def run(self, *paths):
        """
        Returns a path to the given data file within localmh. 
        Considers the following special case for the first argument: 
            
            1. 'systems' the path will be resolved relative to the directory that contains
            external dependencies
            2. 'spec' the path will be resolved relative to the directory that contains
            specifcation dependencies
            3. 'config' the path will be resolved relative to the directory that contains
            the config files
        
        Arguments: 
            *paths
                Set of paths relative to the lmh base directory to be resolved
        Returns: 
            A string representing the path to localmh
        """
        
        # check if we need to replace the first argument
        if len(paths) > 0:
            paths = list(paths)
            if paths[0] == 'systems':
                paths[0] = self._systems
            elif paths[0] == 'spec':
                paths[0] = self._spec
            elif paths[0] == 'config':
                paths[0] = self._config
        
        # and return
        return os.path.join(self._base, *paths)