#!/usr/bin/env python

"""
This file is part of LMH.

LMH is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LMH is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LMH.  If not, see <http://www.gnu.org/licenses/>.
"""

import socket
import subprocess
import glob
import os

from lmh.lib.extenv import java_executable
from lmh.lib.io import std, err
from lmh.lib.repos.local import match_repo
from lmh.lib.git import root_dir
from lmh.lib.env import install_dir


initScript = """
extension info.kwarc.mmt.planetary.PlanetaryPlugin
extension info.kwarc.mmt.planetary.PlanetaryPresenter
extension info.kwarc.mmt.stex.STeXImporter
""";

buildScript = """
archive add {repoPath}
build {repoName} stex-omdoc
build {repoName} planetary
exit
""";

loadScript = """
archive add .

base http://docs.omdoc.org/mmt
""";

mmt_root = os.path.join(install_dir, "ext", "MMT");

def runMMTScript(src, path):
  cp = "{dir}/lib/*:{dir}/mmt/branches/informal/*:{dir}/lfcatalog/*:{dir}/mmt/*".format(dir=mmt_root)
  args = [java_executable, "-Xmx2048m", "-cp", cp, "info.kwarc.mmt.api.frontend.Run"];
  try:
    print src
    comm = subprocess.Popen(args, cwd=path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=src);
    std(comm[0])
    std(comm[1])
  except OSError, o:
    err(o)

def compile(repository):
  std("Generating XHTML in", repository)
  repoName = match_repo(repository)
  repoPath = root_dir(repository)

  src = os.path.join(repoPath, "source")
  script = initScript.format(lmhRoot=install_dir)+"\n"+buildScript.format(repoName=repoName,repoPath=repoPath)
  runMMTScript(script, repoPath)
