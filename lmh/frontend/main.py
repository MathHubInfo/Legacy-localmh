"""
The main entry point for lmh
"""

from typing import List

from lmh.frontend.commander import LMHCommander
from lmh.frontend.standard_commands import StandardCommands

from lmh.manager.manager import LMHManager
from lmh.manager.standard_actions import StandardActions

from lmh.mathhub.manager import MathHubManager
from lmh.mathhub.instance import MathHubInstance
from lmh.mathhub.resolvers.local import LocalMathHubResolver
from lmh.mathhub.resolvers.remote import GitLabResolver

from lmh.systems.manager import SystemManager
from lmh.systems.standard_systems import StandardSystems

from lmh.actions.core.locate import LocateAction

from lmh.config.config import LMHJSONFileConfig
from lmh.config.spec import LMHFileConfigSpec


class LMHMain(object):
    """ The main entry point for lmh. """
    
    @staticmethod
    def make_commander() -> LMHCommander:
        """Creates Creates a new LMHCommander object with the standard configuration. """
        
        # Step 1 : Create an lmh manager
        lmh_manager = LMHManager()
        
        # Step 2: Add a logger and MathHubManager
        from lmh.logger import logger
        lmh_manager.logger = logger.StandardLogger()

        lmh_manager.mathhub = MathHubManager()
        
        # Step 3: Add the LocateAction()
        lmh_manager += LocateAction(systems_dir = 'ext', config_dir = 'bin', spec_dir = 'lmh/data', sty_dir = 'sty')
        
        # Step 4: Setup configuration
        lmh_cfg_spec = LMHFileConfigSpec(lmh_manager('locate', 'spec', 'config.json'))
        lmh_cfg = LMHJSONFileConfig(lmh_cfg_spec, lmh_manager('locate', 'spec', 'lmh.cfg'))
        lmh_manager.config = lmh_cfg
        
        # Step 5: Create a SystemManager()
        lmh_manager.systems = SystemManager(lmh_manager)
        
        # Step 6: Add all standard actions and systems
        StandardActions.register_to(lmh_manager)
        StandardSystems.register_to(lmh_manager.systems)
        
        # Step 7: Create a commander and register standard commands
        lmh_commander = LMHCommander(lmh_manager)
        StandardCommands.register_to(lmh_commander)
        
        # Step 8: Setup Resolvers + MathHub instance
        lr = LocalMathHubResolver(lmh_manager('git'), lmh_manager('locate', 'MathHub'))
        rr = GitLabResolver(lmh_manager('git'), "gl.mathhub.info")
        mhl = MathHubInstance("mathhub.info", lr, rr)
        lmh_manager.mathhub += mhl
        
        # return the commander
        return lmh_commander
    
    @staticmethod
    def main(*args : List[str]) -> None:
        """ Creates an lmh commander, runs it with the given given commands and exits
        with the given exit code. Serves as the main entry point to localmh.

        :arg args: List of parameters to be given to lmh
        """
        import sys
        
        # make the commander object
        lmh_commander = LMHMain.make_commander()
        
        # run it
        code = lmh_commander(*args)
        
        # and exit with the given code
        sys.exit(code)