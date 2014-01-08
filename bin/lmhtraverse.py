import ConfigParser
import os
import lmhutil

def config_load_content(root, config):
  for fl in ["pre", "post"]:
    if config.has_option("gen", fl):
      file_path = os.path.realpath(os.path.join(root, config.get("gen", fl)))
      config.set("gen", "%s_content"%fl, lmhutil.get_file(file_path));

def traverse(root, config):
  files = os.listdir(root)
  print files
  if any(".lmh" in s for s in files):
    newCfg = ConfigParser.ConfigParser()
    newCfg.read(root+"/.lmh")
    config = newCfg
    print "loading config at %s"%root
    config_load_content(root, config)

initConfig = ConfigParser.ConfigParser();

traverse("/home/costea/localmh/MathHub/jucovschi/smglom/source", initConfig)
