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
import lmhutil
import subprocess
import glob
import os


initScript = """
extension info.kwarc.mmt.planetary.PlanetaryPlugin
extension info.kwarc.mmt.stex.STeXImporter
extension info.kwarc.mmt.api.archives.PresentationNarrationExporter html http://cds.omdoc.org/styles/omdoc/mathml.omdoc?html5


mathpath fs http://cds.omdoc.org/styles {lmhRoot}/styles
base http://docs.omdoc.org/mmt
""";

buildScript = """
archive add .
build {repoName} stex-omdoc*
build {repoName} index*
build {repoName} mws-content*
build {repoName} mws-narration*
build {repoName} narration_present_html*
""";

loadScript = """
archive add .

mathpath fs http://cds.omdoc.org/styles {lmhRoot}/styles
base http://docs.omdoc.org/mmt
""";

lmh_root = lmhutil.lmh_root();
mmt_root = lmh_root+"/ext/MMT";

def runMMTScript(src, path):
  cp = "{dir}/lib/*:{dir}/mmt/branches/informal/*:{dir}/lfcatalog/*:{dir}/mmt/*".format(dir=mmt_root)
  args = ["java", "-Xmx2048m", "-cp", cp, "info.kwarc.mmt.api.frontend.Run"];
  try:
    print src 
    comm = subprocess.Popen(args, cwd=path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=src);
    print comm[0]
    print comm[1]
  except OSError, o:
    print o

def compile(repository):
  print "Generating XHTML in %s"%repository
  repoName = lmhutil.lmh_repos(repository)
  repoPath = lmhutil.git_root_dir(repository);

  src = repoPath+"/source"
  script = initScript.format(lmhRoot=lmh_root)+"\n"+buildScript.format(repoName=repoName)
  runMMTScript(script, repoPath)

