import os, os.path

from lmh.external.programs import git
g = git.Git()

from lmh.mathhub.resolvers import local, remote

# build a local resolver
lr = local.LocalMathHubResolver(g, os.path.join(os.getcwd(), "MathHub"))

# and a remote resolver
rr = remote.GitLabResolver(g, "gl.mathhub.info")
