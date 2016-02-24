
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

        import os, os.path
        
        # Step 0: Find the root directory of lmh
        lmh_clone_root = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__), 
                '..', 
                '..'
            )
        )

        # Step 1: Create a MathHub Instance
        from lmh.mathhub import manager as mmanger
        mh_manager = mmanger.MathHubManager(None)

        # Step 2: Create a configuration instance
        from lmh.config import config, spec
        lmh_cfg_spec = spec.LMHFileConfigSpec(os.path.join(lmh_clone_root, "lmh", "data", "config.json"))
        lmh_cfg = config.LMHJSONFileConfig(lmh_cfg_spec, os.path.join(lmh_clone_root, "bin", "lmh.cfg"))

        # Step 3: Create a logger
        from lmh.logger import logger
        SL = logger.StandardLogger()

        # Step 4: Create a manager and register all the standard actions
        from lmh.manager import manager, standard_actions
        lmh_manager = manager.LMHManager(SL, lmh_cfg, mh_manager)
        standard_actions.StandardActions.register_to(lmh_manager)

        # Step 6: Configure MathHub instances
        from lmh.mathhub.resolvers import local, remote
        from lmh.mathhub import instance
        lr = local.LocalMathHubResolver(lmh_manager('git'), os.path.join(lmh_clone_root, "MathHub"))
        rr = remote.GitLabResolver(lmh_manager('git'), "gl.mathhub.info")
        mhl = instance.MathHubInstance("mathhub.info", lr, rr)
        mh_manager.addMathHubInstance(mhl)

        # Step 7: Configure a commander
        from lmh.frontend import commander, standard_commands
        lmh_commander = commander.LMHCommander(lmh_manager)
        standard_commands.StandardCommands.register_to(lmh_commander)
        
        # return the commander
        return lmh_commander
    
    @staticmethod
    def main(*args):
        """
        Creates an lmh commander, runs it with the given commands and exits
        with the given exit code. 
        
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
        