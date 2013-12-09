import lmhutil
import re
import os
import lmhutil
import glob
import subprocess 


def do_status(rep):
  cmd = [lmhutil.which("git"), "status", "-u", "-s"];
  result = subprocess.Popen(cmd, 
                                stdout=subprocess.PIPE,
                                cwd=rep
                               ).communicate()[0]
  if len(result) == 0:
    return

  print rep
  print result

def do(rest):
  if len(rest) == 0:
    rest.append("*/*");

  for repo in rest:
    path = lmhutil.parseRepo(repo);
    for rep in glob.glob(path):
      do_status(rep);
