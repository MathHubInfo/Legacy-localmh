import os, os.path

# Step 1: Create a MathHub Instance
from lmh.mathhub import manager as mmanger
mh_manager = mmanger.MathHubManager(None)

# Step 2: Create a configuration instance
from lmh.config import config, spec
lmh_cfg_spec = spec.LMHFileConfigSpec(os.path.join(os.getcwd(), "lmh", "data", "config.json"))
lmh_cfg = config.LMHJSONFileConfig(lmh_cfg_spec, os.path.join(os.getcwd(), "bin", "lmh.2.cfg"))

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
lr = local.LocalMathHubResolver(lmh_manager('git'), os.path.join(os.getcwd(), "MathHub"))
rr = remote.GitLabResolver(lmh_manager('git'), "gl.mathhub.info")
mhl = instance.MathHubInstance("mathhub.info", lr, rr)
mh_manager.addMathHubInstance(mhl)