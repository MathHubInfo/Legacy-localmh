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

# create a manager
from lmh.mathhub import manager
mh_manager = manager.MathHubManager(None)
mh_manager.addMathHubInstance(mhl)

from lmh.archives import archive
mea = archive.LMHArchive(mhl, "MMT", "examples")
meal = mea.to_local_archive()
meat = meal.manifest