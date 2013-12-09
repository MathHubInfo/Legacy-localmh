import argparse
import glob,os.path
import lmhutil
from subprocess import call

def updateRepo(dir, op):
  if op == "pull" or op == "push":
    print "{1}ing repository {0}".format(dir, op) 
    call([lmhutil.which("git"), op], cwd=dir);
    return
  if op == "upgen":
    try:
      call([lmhutil.which("make"), "-w", "sms", "driver"], cwd=dir+"/source/");
    except Exception as e:
      print e

def updatelmh():
  root = lmhutil.lmh_root()+"/MathHub"
  try:
    call([lmhutil.which("git"), "pull"], cwd=root);
  except Exception as e:
    print e


def do(rest, op):
  parser = argparse.ArgumentParser(description='MathHub repository update tool')
  parser.add_argument('repository', metavar='reps', default=False, nargs='*', help="Repositories to update")

  if op == "pull":
    print "Updating Local MathHub repository"
    updatelmh();

  args, _ = parser.parse_known_args(rest)
  root = lmhutil.lmh_root()+"/MathHub"

  if not args.repository:
    for file in glob.glob(root+"/*/*"):
      if os.path.isfile(file):
        continue
      updateRepo(file, op);

  else:
    for rep in args.repository:
      updateRepo(root+"/"+rep, op);