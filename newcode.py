import os, os.path

# setup external programs
from lmh.external.programs import git
g = git.Git()

# make resolvers
from lmh.mathhub.resolvers import local, remote
lr = local.LocalMathHubResolver(g, os.path.join(os.getcwd(), "MathHub"))
rr = remote.GitLabResolver(g, "gl.mathhub.info")

# and create a local MathHub instance
from lmh.mathhub import instance
mhl = instance.MathHubInstance("mathhub.info", lr, rr)

from lmh.mathhub import manager
mh_manager = manager.MathHubManager(None)
mh_manager.addMathHubInstance(mhl)

# config test

from lmh.config import config, spec
cspec = spec.LMHFileConfigSpec(os.path.join(os.getcwd(), "lmh", "data", "config.json"))
mhc = config.LMHJSONFileConfig(cspec, os.path.join(os.getcwd(), "bin", "lmh2.cfg"))