import lmhconfig
import os
import re

repoRegEx = lmhconfig.repoRegEx;

def init():
  rootdir = lmhconfig.git_root_dir()
  metadir = rootdir+"/META-INF"

  tManifest = lmhconfig.get_template("manifest.tpl")
  tBuild = lmhconfig.get_template("build.tpl")
  tServe = lmhconfig.get_template("serve.tpl")

  if not os.path.exists(metadir):
    os.makedirs(metadir)

  originProp = lmhconfig.git_origin()
  m = re.search(repoRegEx, originProp)
  if m == None:
    print "Could not detect repository group & name"
    return

  [group, name] = m.group(1, 2)

  if not os.path.exists(metadir+"/MANIFEST.MF"):
    lmhconfig.set_file(metadir+"/MANIFEST.MF", tManifest.format(group, name))

  if not os.path.exists(rootdir+"/build.msl"):
    lmhconfig.set_file(rootdir+"/build.msl", tBuild.format(group, name, lmhconfig.lmh_root()))

  if not os.path.exists(rootdir+"/serve.msl"):
    lmhconfig.set_file(rootdir+"/serve.msl", tServe.format(group, name, lmhconfig.lmh_root()))
