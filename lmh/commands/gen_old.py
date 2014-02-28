
# ===
# ALLTEX
# ===

def gen_alltex(dest, mods, config, args, msg):
  # generates all.tex
  if not config.has_option("gen", "pre_content") or not config.has_option("gen", "post_content"):
    return

  msg("GEN_ALLTEX: "+dest)

  preFileContent = config.get("gen", "pre_content")
  postFileContent = config.get("gen", "post_content")
  content = [];
  for mod in mods:
    content.append(all_modtpl.substitute(file=mod["modName"]));

  text = all_textpl.substitute(pre_tex=preFileContent, post_tex=postFileContent, mods="\n".join(content))

  if args.simulate:
    print "echo -n "+util.shellquote(text) + " > "+util.shellquote(dest)
    return

  output = open(dest, "w")
  output.write(text)
  output.close()

def gen_ext(extension, root, mods, config, args, todo, force, msg):
  # find and add files to todo
  if len(args) == 0:
    msg("GEN_EXT_MODS_"+extension.upper()+": "+root)
    for mod in mods:
      modName = mod["modName"]
      modFile = root+"/"+modName+"."+extension

      if force or not os.path.exists(modFile) or os.path.getmtime(mod["file"]) > os.path.getmtime(modFile):
        msg("GEN_EXT_TODO_"+extension.upper()+": "+modFile)
        todo.append({"root": root, "modName": mod["modName"], "pre" : config.get("gen", "pre"), "post" : config.get("gen", "post")})
  else:
    msg("GEN_EXT_ARGS_"+extension.upper()+": "+root)
    for omdoc in args:
      if omdoc.endswith("."+extension):
        omdoc = omdoc[:-len(extension)-1];
      if omdoc.endswith(".tex"):
        omdoc = omdoc[:-4];
      omdoc = os.path.basename(omdoc)
      msg("GEN_EXT_TODO_"+extension.upper()+": "+omdoc)
      todo.append({"root": root, "modName": omdoc, "pre" : config.get("gen", "pre"), "post" : config.get("gen", "post") })

# ===
# OMDOC
# ===

def gen_omdoc_runner(args, omdoc):
  try:
    current = multiprocessing.current_process()
    wid = current._identity[0]
    def msg(m):
      if args.debug:
        print "# "+ m 
    run_gen_omdoc(omdoc["root"], omdoc["modName"], omdoc["pre"], omdoc["post"], msg, port=3353+wid, args=args)
  except Exception as e:
    print e
    print "WARNING: Generating OMDoc failed. (Make sure latexml is running)"

def gen_omdoc(docs, args, msg):
  if args.simulate:
    print "#---------------"
    print "# generate omdoc"
    print "#---------------"
    print "export STEXSTYDIR=\""+util.stexstydir+"\""
    print "export PATH=\""+util.perl5bindir+"\":$PATH"
    print "export PERL5LIB=\""+util.perl5libdir+"\":$PERL5LIB"
    for omdoc in docs:
      run_gen_omdoc(omdoc["root"], omdoc["modName"], omdoc["pre"], omdoc["post"], msg, port=3353, args=args)
    return True
  elif len(docs) == 0:
    print "Master: no omdoc to generate, skipping omdoc generation ..." 
    return True
  else:
    print "Master: Generating OmDoc for", len(docs), "file(s). " 
    done = False

    pool = multiprocessing.Pool(processes=args.workers)
    try:
      result = pool.map_async(functools.partial(gen_omdoc_runner, args), docs).get(9999999)
      try:
        res = result.get(9999999)
      except:
        pass
      res = True
    except KeyboardInterrupt:
      print "Master: received <<KeyboardInterrupt>>"
      print "Master: killing worker processes ..."
      pool.terminate()
      print "Master: Cleaning up latexmls processes ..."
      try:
        p = Popen(['ps', '-A'], stdout=PIPE)
        out, err = p.communicate()
        for line in out.splitlines():
          if 'latexmls' in line:
           pid = int(line.split(None, 1)[0])
           os.kill(pid, signal.SIGKILL)
      except Exception as e:
        print e
        print "Master: Unable to kill some latexmls processes. "
      print "Master: Waiting for all processes to finish ..."
      time.sleep(5)
      print "Master: Done. "
      res = False
    pool.close()
    pool.join()
    print "Master: All worker processes have finished. "
    return res
    

def run_gen_omdoc(root, mod, pre_path, post_path, msg, args=None, port=3354):
  msg("GEN_OMDOC: "+ mod + ".omdoc")
  oargs = args
  args = [latexmlc,"--expire=120", "--port="+str(port), "--profile", "stex-module", "--path="+stydir, mod+".tex", "--destination="+mod+".omdoc", "--log="+mod+".ltxlog"];

  if needsPreamble(root+"/"+mod+".tex"):
    args.append("--preamble="+pre_path)
    args.append("--postamble="+post_path)

  if oargs.simulate:
    print "cd "+util.shellquote(root)
    print " ".join(args)
    return 

  wid = port - 3353

  _env = os.environ
  _env = util.perl5env(_env)

  
  try:
    print "Worker #"+str(wid)+": Generating OMDoc for "+os.path.relpath(root)+"/"+mod+".tex"
    p = Popen(args, cwd=root, env=_env, stdin=None, stdout=PIPE, stderr=PIPE, preexec_fn=os.setsid)
    out, err = p.communicate()
    for line in out.split("\n"):
      if line != "":
        print "Worker #"+str(wid)+": "+line
    for line in err.split("\n"):
      if line != "":
        print "Worker #"+str(wid)+": "+line
    print "Worker #"+str(wid)+": Generated OMDoc for "+os.path.relpath(root)+"/"+mod+".tex"
    parseLateXMLOutput(root+"/"+mod+".tex")
  except KeyboardInterrupt:
    print "Worker #"+str(wid)+": Sending SIGINT to latexml..."
    try:
      util.kill_child_processes(p.pid,sig=signal.SIGINT, self=True)
      p.kill()
    except Exception as e:
      print e
    print "Worker #"+str(wid)+": terminated latexml. "
    sys.exit()

# ===
# PDF
# ===

def gen_pdf_runner(args, pdf):
  try:
    current = multiprocessing.current_process()
    wid = current._identity[0]
    def msg(m):
      if args.debug:
        print "# "+ m 
    run_gen_pdf(pdf["root"], pdf["modName"], pdf["pre"], pdf["post"], msg, port=3353+wid, args=args)
  except Exception as e:
    print e
    print "WARNING: Generating PDF failed. (Make sure pdflatex is running)"

def gen_pdf(docs, args, msg):
  if args.simulate:
    print "#---------------"
    print "# generate pdf"
    print "#---------------"
    print "export TEXINPUTS="+TEXINPUTS
    for pdf in docs:
      run_gen_pdf(pdf["root"], pdf["modName"], pdf["pre"], pdf["post"], msg, port=3353, args=args)
    return True
  elif len(docs) == 0:
    print "Master: no pdf to generate, skipping pdf generation ..." 
    return True
  else:
    print "Master: Generating pdf for", len(docs), "file(s). " 
    done = False

    pool = multiprocessing.Pool(processes=args.workers)
    try:
      result = pool.map_async(functools.partial(gen_pdf_runner, args), docs).get(9999999)
      try:
        res = result.get(9999999)
      except:
        pass
      res = True
    except KeyboardInterrupt:
      print "Master: received <<KeyboardInterrupt>>"
      pool.terminate()
      print "Master: Waiting for all processes to finish ..."
      print "Master: Done. "
      res = False
    pool.close()
    pool.join()
    print "Master: All worker processes have finished. "
    return res
    

def run_gen_pdf(root, mod, pre_path, post_path, msg, args=None, port=3354):
  msg("GEN_PDF: "+ mod + ".pdf")
  modPath = os.path.join(root, mod)
  if args.simulate:
    print "cd "+util.shellquote(root)
    if needsPreamble(root+"/"+mod+".tex"):
      print "echo \"\\begin{document}\\n\" | cat "+util.shellquote(pre_path)+" - "+util.shellquote(modPath+".tex")+" "+util.shellquote(post_path)+" | "+pdflatex+" -jobname " + mod 
    else:
      print pdflatex+" "+util.shellquote(mod+".tex")
    return 

  wid = port - 3354

  print "Worker #"+str(wid)+": generating "+mod+".pdf"
  try:
    if needsPreamble(root+"/"+mod+".tex"):
      p0 = Popen(["echo", "\\begin{document}\n"], stdout=PIPE)
      c1 = ["cat", pre_path, "-", modPath+".tex", post_path]
      p1 = Popen(c1, cwd=root, stdin=p0.stdout, stdout=PIPE)
      p2 = Popen([pdflatex, "-jobname", mod], cwd=root, stdin=p1.stdout, stdout=PIPE, env = {"TEXINPUTS" : TEXINPUTS})
    else:
      p2 = Popen([pdflatex, mod+".tex"], cwd=root, stdout=PIPE, env = {"TEXINPUTS" : TEXINPUTS})

    output = p2.communicate()[0]
    if args.debug:
      print "Worker #"+str(wid)+": "+output
    if not p2.returncode == 0:
      print "Worker #"+str(wid)+": failed to generate "+mod+".pdf"
      print output
    else:
      print "Worker #"+str(wid)+": generated "+mod+".pdf"
    util.set_file(modPath+".clog", output)
  except KeyboardInterrupt:
    sys.exit()
    

# ===
# General generation stuffs
# ===

def prep_gen(dir_or_path, args, msg):
  # prepare generation
  rep = dir_or_path # use the repository in the dir or path

  # intialise this repository
  rep_root = util.git_root_dir(rep)
  repo_name = util.lmh_repos(rep)

  # have todo lists
  omdocToDo = []
  pdfToDo = []

  def traverse(root, config):

    # traversing a directory
    files = os.listdir(root)

    # go into subdirectories
    for d in filter((lambda x: os.path.isdir(root+"/"+x)), files):
      traverse(root+"/"+d, config)

    msg("TRAVERSE: "+root)

    # load the config files if possible
    if any(".lmh" in s for s in files):
      newCfg = ConfigParser.ConfigParser()
      try:
        newCfg.read(root+"/.lmh")
        config = newCfg
        config_load_content(root, config)
      except:
        print "WARNING: Failed to load config at %s"%root

    # LOAD the modules
    mods = get_modules(root, files, msg)

    if len(mods) > 0:
      # find the youngest mod
      youngest = max(map(lambda x : x["date"], mods))

      # generate sms
      gen_sms_all(root, mods, args, msg)

      # find the localpaths and all .tex files
      allTex = root+"/all.tex"
      localPathTex = root+"/localpaths.tex"

      if not args.update or not os.path.exists(localPathTex) or youngest > os.path.getmtime(localPathTex):
        gen_localpaths(localPathTex, rep_root, repo_name, args, msg)

        if not args.update or not os.path.exists(allTex) or youngest > os.path.getmtime(allTex):
          gen_alltex(allTex, mods, config, args, msg)


        if args.omdoc != None:          
          if config.has_option("gen", "pre_content"):
            gen_ext("omdoc", root, mods, config, args.omdoc, omdocToDo, not args.update, msg)
          else:
            print "WARNING: GEN_EXT_OMDOC: OMDoc generation desired but could not find preamble and/or postamble - skipping generation"
      
        if args.pdf != None:
          if config.has_option("gen", "pre_content"):
            gen_ext("pdf", root, mods, config, args.pdf, pdfToDo, not args.update, msg);
          else:
            print "WARNING: GEN_EXT_PDF: PDF generation desired but could not find preamble and/or postamble - skipping generation"

  # go into the source directory if you are in the root
  if rep == rep_root:
    rep = rep + "/source"

  if not os.path.exists(rep):
    msg("WARNING: Directory does not exist: %r"%rep)
    return ([], [])


  # create the configuration files
  initConfig = ConfigParser.ConfigParser()
  initConfig.add_section("gen")

  for fl in ["pre", "post"]:
    fn = rep_root+"/lib/%s.tex"%fl
    if os.path.exists(fn):
      msg("ADD_CONFIG: Found '"+fl+"': "+fn)
      initConfig.set("gen", fl, fn)

  # load the configuration
  config_load_content(rep, initConfig, msg)

  # traverse this directory
  traverse(rep, initConfig)

  try:
    if args.low:
      msg("NOTICE: Using low priority")
      util.lowpriority()
  except Exception as e:
    print e
    print "WARNING: Failed to set low priority!"

  return (omdocToDo, pdfToDo)

def run_gen(omdocToDo, pdfToDo, args, msg):
  # generate all omdoc
  omdoc = gen_omdoc(omdocToDo, args, msg)
  if not omdoc:
    print "OmDoc generation aborted prematurely, skipping pdf generation. "
    return

  pdf = gen_pdf(pdfToDo, args, msg)
  if not pdf:
    print "PDF generation aborted prematurely. "
    return




def config_load_content(root, config, msg):
  # Load config content
  msg("CONFIG_LOAD_CONTENT: "+root)
  for fl in ["pre", "post"]:
    if config.has_option("gen", fl):
      file_path = os.path.realpath(os.path.join(root, config.get("gen", fl)))
      config.set("gen", "%s_content"%fl, util.get_file(file_path))

def get_modules(root, files, msg):
  # finds all the modules in root
  mods = []
  msg("GET_MODULES: "+root)
  for file in filter(lambda x: os.path.isfile(root+"/"+x), files):
    fullFile = root+"/"+file
    if not file.endswith(".tex") or file in special_files or not util.effectively_readable(fullFile):
      # skip it if it is in special_files
      continue
    msg("FIND_MODULE: Found "+fullFile)
    mods.append({ "modName" : file[:-4], "file": fullFile, "date": os.path.getmtime(fullFile)})
  return mods