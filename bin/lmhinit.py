import lmhutil
import os
import re

repoRegEx = lmhutil.repoRegEx;

def init():
  rootdir = lmhutil.git_root_dir()
  metadir = rootdir+"/META-INF"

  tManifest = lmhutil.get_template("manifest.tpl")
  tBuild = lmhutil.get_template("build.tpl")
  tServe = lmhutil.get_template("serve.tpl")

  if not os.path.exists(metadir):
    os.makedirs(metadir)

  originProp = lmhutil.git_origin()
  m = re.search(repoRegEx, originProp)
  if m == None:
    print "Could not detect repository group & name"
    return

  [group, name] = m.group(1, 2)

  if not os.path.exists(metadir+"/MANIFEST.MF"):
    lmhutil.set_file(metadir+"/MANIFEST.MF", tManifest.format(group, name))

  if not os.path.exists(rootdir+"/build.msl"):
    lmhutil.set_file(rootdir+"/build.msl", tBuild.format(group, name, lmhutil.lmh_root()))

  if not os.path.exists(rootdir+"/serve.msl"):
    lmhutil.set_file(rootdir+"/serve.msl", tServe.format(group, name, lmhutil.lmh_root()))
