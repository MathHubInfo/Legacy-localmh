import lmhconfig
import os
from subprocess import call

def setup():
  root = lmhconfig.lmh_root()+"/ext"
  os.chdir(root)

  gitpath = lmhconfig.which("git")
  svnpath = lmhconfig.which("svn")

  print "cloning LaTeXML"
  call([gitpath, "clone", "https://github.com/KWARC/LaTeXML.git"])
  call([svnpath, "co", "https://svn.kwarc.info/repos/stex/"])
  