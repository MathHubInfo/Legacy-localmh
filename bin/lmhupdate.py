import argparse
import glob,os.path
import lmhconfig
from subprocess import call

def updateRepo(dir, op):
  print "updating {0}".format(dir) 
  call([lmhconfig.which("git"), "pull"], cwd=dir);

def do(rest, op):
  parser = argparse.ArgumentParser(description='MathHub repository update tool')
  parser.add_argument('repository', metavar='reps', default=False, nargs='*', help="Repositories to update")

  args, _ = parser.parse_known_args(rest)
  root = lmhconfig.lmh_root()+"/MathHub"

  if not args.repository:
    for file in glob.glob(root+"/*/*"):
      if os.path.isfile(file):
        continue
      updateRepo(file, op);

  else:
    for rep in args.repository:
      updateRepo(root+"/"+rep, op);