

def install_autocomplete():
	err("Autocomplete auto-installer is currently disabled. ")
	err("Please install it manually from https://github.com/kislyuk/argcomplete.git")
	return False
	# TODO: Fix me
	#root = util.lmh_root()+"/ext"
	#util.git_clone(root, "https://github.com/kislyuk/argcomplete.git", "arginstall")
	#call([python, "setup.py", "install", "--user"], cwd=root+"/arginstall")
	#activatecmd = root+"/arginstall/scripts/activate-global-python-argcomplete";
	#print "running %r"%(activatecmd)
	#call([root+"/arginstall/scripts/activate-global-python-argcomplete"])

#
# Main Setup Routines
#

def run_setup(args):
	"""Perform various setup functions"""

	# Check dependencies first
	if (not args.force) and (not check_deps()):
		err("Dependency check failed, either install dependencies manually ")
		err("or use --force to ignore dependency checks. ")
		return False


	action = args.m_action

	if action == "":
		# If there is nothing special to do, install everything
		if args.latexml_action == "" and args.stex_action == "" and args.mmt_action == "" and args.latexmls_action == "" and args.latexmlstomp_action == "":
			action = "in"
		else:
			action = "sk"

	# LaTeXML: git, cpanm
	latexml_source = get_config("setup::latexml::source")
	latexml_branch = get_config("setup::latexml::branch")
	(success, latexml_source, latexml_branch) = git_run_setup("LaTeXML", args.latexml_action, True, args.latexml_source, ext_dir, action, latexml_source, latexml_branch)
	if not success:
		return False

	# LaTeXMLs: git, cpanm
	latexmls_source = get_config("setup::latexmls::source")
	latexmls_branch = get_config("setup::latexmls::branch")
	(success, latexmls_source, latexmls_branch) = git_run_setup("LaTeXMLs", args.latexmls_action, True, args.latexmls_source, ext_dir, action, latexmls_source, latexmls_branch)
	if not success:
		return False

	# LaTeXMLStomp: git, cpanm
	latexmlstomp_source = get_config("setup::latexmlstomp::source")
	latexmlstomp_branch = get_config("setup::latexmlstomp::branch")
	(success, latexmlstomp_source, latexmlstomp_branch) = git_run_setup("LaTeXMLStomp", args.latexmlstomp_action, True, args.latexmlstomp_source, ext_dir, action, latexmlstomp_source, latexmlstomp_branch)
	if not success:
		return False

	# sTeX: git, no cpanm
	stex_source = get_config("setup::stex::source")
	stex_branch = get_config("setup::stex::branch")
	(success, stex_source, stex_branch) = git_run_setup("sTeX", args.stex_action, False, args.stex_source, ext_dir, action, stex_source, stex_branch)
	if not success:
		return False

	# MMT: svn, no cpanm
	mmt_source = get_config("setup::mmt::source")
	mmt_branch = get_config("setup::mmt::branch")
	(success, mmt_source, mmt_branch) = svn_run_setup("MMT", args.mmt_action, False, args.mmt_source, ext_dir, action, mmt_source, mmt_branch)
	if not success:
		return False

	# Store all the selcted sources back in the config.
	if args.store_source_selections:
		set_config("setup::latexml::source", latexml_source)
		set_config("setup::latexml::branch", latexml_branch)

		set_config("setup::latexmls::source", latexmls_source)
		set_config("setup::latexmls::branch", latexmls_branch)

		set_config("setup::latexmlstomp::source", latexmls_source)
		set_config("setup::latexmlstomp::branch", latexmls_branch)

		set_config("setup::stex::source", stex_source)
		set_config("setup::stex::branch", stex_branch)

		set_config("setup::mmt::source", mmt_source)
		set_config("setup::mmt::branch", mmt_branch)

	if args.autocomplete:
		std("Installing autocomplete ...")
		install_autocomplete()

	if args.add_private_token and len(args.add_private_token) == 1:
		std("Adding private token ...")
		set_config("gl::private_token", args.add_private_token[0])

	return True
