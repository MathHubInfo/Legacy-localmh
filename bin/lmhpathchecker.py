import lmhpath;
import lmhutil;
import os;
import difflib;
import fileinput

mathroot = lmhutil.lmh_root()+"/MathHub";
fileIndex = {};
remChoices = {};

def replaceFnc(fullPath, m):
  if os.path.exists(mathroot+"/"+m.group(1)+".tex"):  # link is ok
    return m.group(0);

  print "in ",fullPath, ": path ", m.group(1), "is invalid";

  if m.group(0) in remChoices:
    print "Remembered replacement to "+remChoices[m.group(0)];
    return remChoices[m.group(0)];

  comps = m.group(1).split("/");
  fileName = comps[len(comps)-1]+".tex";
  if not fileName in fileIndex:
    print "Error: No suitable index file found "+fileName;
    return m.group(0);

  results = [];
  for validPath in fileIndex[fileName]:
    cnt = 0;
    s = difflib.SequenceMatcher(None, validPath, m.group(1))
    results.append((s.ratio(), validPath));

  results = sorted(results, key=lambda result: result[0], reverse=True)

  print "Possible results: "
  print "1 ) Don't change"

  for idx, result in enumerate(results):
    print idx+2,")",result[1]

  while True:
    choice = raw_input('Enter your input:')
    try:
      choice = int(choice)
    except ValueError:
      print "invalid choice"
      continue
    if choice < 1 or choice > len(results) + 1:
      print "Not valid choice"
    break

  while True:
    remember = raw_input('Remember choice (y/n)?:')
    if remember == 'y' or remember == "n":
      break
    print "invalid choice";

  result = m.group(0);

  if choice > 1:
    replacePath = results[choice - 2][1][:-4];
    result = "MathHub{"+replacePath+"}";

  if remember == 'y':
    remChoices[m.group(0)] = result;

  return m.group(0);

def checkpaths(dir="."):
  print "creating index";
  for root, dirs, files in os.walk(mathroot):
    for file in files:
      if not file.endswith(".tex"):
        break;

      if file not in fileIndex:
        fileIndex[file]=[];

      fileIndex[file].append(root[len(mathroot)+1:]+"/"+file);

  lmhpath.replacePath(dir, replaceFnc, False);

def do(rest):
  if len(rest) == 0:
    checkpaths(mathroot)

  checkpaths(rest[0])  