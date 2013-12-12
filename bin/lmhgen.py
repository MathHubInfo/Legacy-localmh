"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhgen
   :func: create_parser
   :prog: lmhgen

"""

import argparse
import lmhutil
import os
import glob
from subprocess import call
import re
import time
import datetime
from string import Template

from multiprocessing import Pool
import multiprocessing 

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Generation tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('gen', formatter_class=argparse.RawTextHelpFormatter, help='updates generated content')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository
  parser.add_argument('--omdoc', nargs="*", help="generate omdoc files")
  # parser.add_argument('--pdf', nargs="*", help="generate pdf files")
  parser.add_argument('-f', '--force', const=True, default=False, action="store_const", help="force all regeneration")
  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

#\begin{module}....
#\end{module}
#\begin{importmodulevia}...
#\end{importmodulevia}

#\symdef...
#\abbrdef...
#\symvariant...
#keydef
#\listkeydef
#\importmodule...
#\gimport...
#\adoptmodule...
#\importmhmodule
#\adoptmhmodule

regStrings = [r'\\(symdef|abbrdef|symvariant|keydef|listkeydef|importmodule|gimport|adoptmodule|importmhmodule|adoptmhmodule)', r'\\begin{(module|importmodulevia)}', r'\\end{(module|importmodulevia)}']
regs = map(re.compile, regStrings)

all_textpl = Template(lmhutil.get_template("alltex_struct.tpl"))
all_modtpl = Template(lmhutil.get_template("alltex_mod.tpl"))
all_pathstpl = Template(lmhutil.get_template("localpaths.tpl"))
lmh_root = lmhutil.lmh_root()
special_files = {"all.tex":True, "localpaths.tex": True};

latexmlc = lmhutil.which("latexmlc")
stexstydir = lmh_root+"/ext/sTeX/sty";
stydir = lmh_root+"/sty";

def genOMDoc(root, mod, pre_path, port=3354):
  print "generating %r"%(mod+".omdoc")
  args = [latexmlc,"--expire=120", "--port="+str(port), "--profile", "stex-module", "--path="+stydir, "--preload="+pre_path, mod+".tex", "--destination="+mod+".omdoc", "--log="+mod+".ltxlog"];
  call(args, cwd=root, env={"STEXSTYDIR" : stexstydir})

def genSMS(input, output):
  print "generating %r"%output
  output = open(output, "w")
  for line in open(input):
    for reg in regs:
      if reg.search(line):
        output.write(line.strip()+"%\n")
        break
  output.close()

def genAllTex(dest, files, preFileContent, postFileContent):
  if preFileContent == None or postFileContent == None:
    return
  print "generating %r"%dest
  mods = [];
  for file in files:
    if not file.endswith(".tex") or file == "all.tex":
      continue
    mods.append(all_modtpl.substitute(file=file[:-4]));

  output = open(dest, "w")
  output.write(all_textpl.substitute(pre_tex=preFileContent, post_tex=postFileContent, mods="\n".join(mods)))
  output.close()

def genLocalPaths(dest, repo, repo_name):
  print "generating %r"%dest
  output = open(dest, "w")
  output.write(all_pathstpl.substitute(mathhub=lmh_root, repo=repo, repo_name=repo_name))
  output.close()

def get_modules(root, files):
  mods = [];
  for file in files:
    if not file.endswith(".tex") or file in special_files:
      continue
    
    fullFile = root+"/"+file;
    mods.append({ "modName" : file[:-4], "file": fullFile, "date": os.path.getmtime(fullFile)})
  return mods

def do_compute(omdoc):
  current = multiprocessing.current_process()
  wid = current._identity[0]
  print str(datetime.datetime.now().time())+" worker "+str(wid)+": "+omdoc["modName"]+" "
  genOMDoc(omdoc["root"], omdoc["modName"], omdoc["pre"], 3353+wid)

def do_bulk_omdoc(omdocs):
  if len(omdocs) < 10:
    for omdoc in omdocs:
      genOMDoc(omdoc["root"], omdoc["modName"], omdoc["pre"])
    return

  processes = 8;

  pool = Pool(processes=processes)
  result = pool.map(do_compute, omdocs)


def do_gen(rep, args):
  print "generating in repository %r"%rep
  rep_root = lmhutil.git_root_dir(rep);

  repo_name = lmhutil.lmh_repos(rep)

  preFilePath = rep_root+"/lib/pre.tex"
  postFilePath = rep_root+"/lib/post.tex"

  omdocToDo = [];
  preFileContent = postFileContent = None

  if not os.path.exists(preFilePath):
    print "Warning: could not find pre file. Only limited generation will occur"
  else :
    preFileContent = lmhutil.get_file(preFilePath);

  if not os.path.exists(postFilePath):
    print "Warning: could not find post file. Only limited generation will occur"
  else:
   postFileContent = lmhutil.get_file(postFilePath);

  if rep == rep_root:
    rep = rep + "/source";

  for root, dirs, files in os.walk(rep):
    mods = get_modules(root, files)
    if len(mods) == 0:
      continue

    youngest = mods[0]["date"]
    for mod in mods:
      if mod["date"] > youngest:
        youngest = mod["date"]

    # Generate all SMS files
    for mod in mods:
      smsfileName = root+"/"+mod["modName"]+".sms";

      if args.force or not os.path.exists(smsfileName) or mod["date"] > os.path.getmtime(smsfileName):
        genSMS(mod["file"], smsfileName)
        continue

    allTex = root+"/all.tex";
    localPathTex = root+"/localpaths.tex"
 
    if args.force or not os.path.exists(localPathTex) or youngest > os.path.getmtime(localPathTex):
      genLocalPaths(localPathTex, rep_root, repo_name);

    if args.force or not os.path.exists(allTex) or youngest > os.path.getmtime(allTex):
      genAllTex(allTex, files, preFileContent, postFileContent);

    if args.omdoc != None and preFileContent != None:
      if len(args.omdoc) == 0:
        for mod in mods:
          modName = mod["modName"]
          modFile = root+"/"+modName+".omdoc";

          if args.force or not os.path.exists(modFile) or os.path.getmtime(mod["file"]) > os.path.getmtime(modFile):
            omdocToDo.append({"root": root, "modName": mod["modName"], "pre" : preFilePath})
      else:
        for omdoc in args.omdoc:
          if not omdoc.endswith(".omdoc"):
            print "%r is not a vaid omdoc file name"%omdoc
            continue
          omdocToDo.append({"root": root, "modName": omdoc[:-6], "pre" : preFilePath })
      
  do_bulk_omdoc(omdocToDo)

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.parseRepo(".")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_gen(rep, args);