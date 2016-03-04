
class LMHMain(object):
    """
    The main entry point for lmh.
    """
    
    @staticmethod
    def make_commander():
        """
        Creates a new LMHCommander object with the standard configuration. 
        
        Returns: 
            a new LMHCommander() object
        """
        
        # Step 1 : Create an lmh manager
        from lmh.manager import manager
        lmh_manager = manager.LMHManager()
        
        # Step 2: Add a logger and MathHubManager
        from lmh.logger import logger
        lmh_manager.logger = logger.StandardLogger()
        
        from lmh.mathhub import manager as mmanger
        lmh_manager.mathhub = mmanger.MathHubManager()
        
        # Step 3: Add the LocateAction()
        from lmh.actions.core import locate
        lmh_manager += locate.LocateAction(systems_dir = 'ext', config_dir = 'bin', spec_dir = 'lmh/data')
        
        # Step 4: Setup configuration
        from lmh.config import config, spec
        lmh_cfg_spec = spec.LMHFileConfigSpec(lmh_manager('locate', 'spec', 'config.json'))
        lmh_cfg = config.LMHJSONFileConfig(lmh_cfg_spec, lmh_manager('locate', 'spec', 'lmh.cfg'))
        lmh_manager.config = lmh_cfg
        
        # Step 5: Create a SystemManager()
        from lmh.systems import manager as smanager
        lmh_manager.systems = smanager.SystemManager(lmh_manager)
        
        # Step 6: Add all standard actions and systems
        from lmh.manager import standard_actions
        standard_actions.StandardActions.register_to(lmh_manager)
        
        from lmh.systems import standard_systems
        standard_systems.StandardSystems.register_to(lmh_manager.systems)
        
        # Step 7: Create a commander and register standard commands
        from lmh.frontend import commander, standard_commands
        lmh_commander = commander.LMHCommander(lmh_manager)
        standard_commands.StandardCommands.register_to(lmh_commander)
        
        # Step 8: Setup Resolvers + MathHub instance
        from lmh.mathhub.resolvers import local, remote
        from lmh.mathhub import instance
        lr = local.LocalMathHubResolver(lmh_manager('git'), lmh_manager('locate', 'MathHub'))
        rr = remote.GitLabResolver(lmh_manager('git'), "gl.mathhub.info")
        mhl = instance.MathHubInstance("mathhub.info", lr, rr)
        lmh_manager.mathhub += mhl
        
        # return the commander
        return lmh_commander
    
    @staticmethod
    def main(*args):
        """
        Creates an lmh commander, runs it with the given commands and exits
        with the given exit code. Serves as the main entry point to localmh. 
        
        Arguments:
            *args
                Arguments to give to the lmh_commander
        """
        import sys
        
        # make the commander object
        lmh_commander = LMHMain.make_commander()
        
        # run it
        code = lmh_commander(*args)
        
        # and exit with the given code
        sys.exit(code)
        