import lmhconfig
import os
from subprocess import call

def setup():
  root = lmhconfig.lmh_root()+"/ext"
  os.chdir(root)

  gitpath = lmhconfig.which("git")

  print "cloning LaTeXML"
  call([gitpath, "clone", "https://github.com/KWARC/LaTeXML.git"])
  print "cloning sTeX"
  call([gitpath, "clone", "https://github.com/KWARC/sTeX.git"])
  