import socket
import lmhutil
import subprocess
import glob

port = 8081;

initScript = """
extension info.kwarc.mmt.planetary.PlanetaryPlugin
extension info.kwarc.mmt.stex.STeXImporter

mathpath fs http://cds.omdoc.org/styles {lmhRoot}/styles
base http://docs.omdoc.org/mmt
""";

buildScript = """
archive add .
build {repoName} stex-omdoc*
build {repoName} index*
build {repoName} mws-content*
build {repoName} mws-narration*
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
    out = subprocess.Popen(args, cwd=path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=src)[0];
    #print out
  except OSError, o:
    print o

def compile(repository):
  repoName = repository.split("/")[1];
  repoPath = "%s/MathHub/%s"%(lmh_root, repository)
  src = repoPath+"/source"
  script = initScript.format(lmhRoot=mmt_root)+"\n"+buildScript.format(repoName=repoName)
  runMMTScript(script, repoPath)

  #genScript = loadScript.format(mmtRoot=mmt_root, lmhRoot=lmh_root);
  #for list in glob.glob(src+"/*.omdoc"):
  #  name = list[len(src)+1:-6]
  #  omdoc = "http://mathhub.info/smglom/smglom/"+name
  #  getU = "get %s.omdocf?%s? present http://cds.omdoc.org/styles/omdoc/mathml.omdoc?html5 write %s/%s.html"%(omdoc, name, src, name);
  #  genScript += getU + "\n";
  #lmhutil.set_file(repoPath+"/gen.msl", genScript)
  #runMMTScript(genScript, repoPath)  

#compile("smglom/smglom")