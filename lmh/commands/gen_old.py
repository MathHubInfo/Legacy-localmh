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