import lmhconfig
import os
from subprocess import call

def setup():
  root = lmhconfig.lmh_root()+"/ext"
  os.chdir(root)

  gitpath = lmhconfig.which("git")

  print "cloning LaTeXML"
  call([gitpath, "clone", "git@github.com:KWARC/LaTeXML.git"])
  