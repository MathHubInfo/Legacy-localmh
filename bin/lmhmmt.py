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

