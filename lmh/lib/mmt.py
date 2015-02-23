import socket
import subprocess
import glob
import os
import re

from lmh.lib.extenv import java_executable
from lmh.lib.io import std, err
from lmh.lib.repos.local import match_repo
from lmh.lib.git import root_dir
from lmh.lib.env import install_dir, data_dir


initScript = """
extension info.kwarc.mmt.planetary.PlanetaryPlugin
extension info.kwarc.mmt.planetary.PlanetaryPresenter
extension info.kwarc.mmt.stex.STeXImporter
""";

buildScript = """
archive add {repoPath}
build {repoName} stex-omdoc {fileName}
build {repoName} planetary http..mathhub.info/{repoName}/{fileName}
exit
""";

loadScript = """
archive add .

base http://docs.omdoc.org/mmt
""";

mmt_root = os.path.join(install_dir, "ext", "MMT")

def runMMTScript(src, path, filename):
    cp = "{dir}/lib/*:{dir}/main/branches/informal/*:{dir}/lfcatalog/*:{dir}/main/*".format(dir=mmt_root)
    args = [java_executable, "-Xmx2048m", "-cp", cp, "info.kwarc.mmt.api.frontend.Run"];
    try:
        comm = subprocess.Popen(args, cwd=path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate(input=src)
        #std(comm[0])
        #err(comm[1])
        if len(comm[1]) != 0:
            return False
        else:
            return True
    except OSError as o:
        err(o)
        return False

def runMMTScript_dump(src, path, filename):
    cp = "{dir}/lib/*:{dir}/main/branches/informal/*:{dir}/lfcatalog/*:{dir}/main/*".format(dir=mmt_root)
    args = [java_executable, "-Xmx2048m", "-cp", cp, "info.kwarc.mmt.api.frontend.Run"]

    std("cd", path)
    std("cat <<EOF |", " ".join(args), "\n", str(src), "\nEOF")

    return True


def compile(repository, filename):

    # Find the repo paths
    repoName = match_repo(repository)
    repoPath = match_repo(repository, abs=True)
    src = os.path.join(repoPath, "source")
    # What do we need to do?
    script = initScript.format(lmhRoot=install_dir)+"\n"+buildScript.format(repoName=repoName,repoPath=repoPath,fileName=filename)

    # Lets run it.
    return runMMTScript(script, repoPath, filename)

def compile_dump(repository, filename):
    # Find the repo paths
    repoName = match_repo(repository)
    repoPath = match_repo(repository, abs=True)
    src = os.path.join(repoPath, "source")
    # What do we need to do?
    script = initScript.format(lmhRoot=install_dir)+"\n"+buildScript.format(repoName=repoName,repoPath=repoPath,fileName=filename)

    # Lets run it.
    return runMMTScript_dump(script, repoPath, filename)
