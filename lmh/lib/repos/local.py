"""
This file is part of LMH.

LMH is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LMH is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LMH.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import re
import os.path
import glob
import functools

from string import Template

from lmh.lib.env import install_dir, data_dir
from lmh.lib.io import term_colors, std, std_paged, err, copytree, write_file, read_file, read_file_lines
from lmh.lib.repos import is_valid_repo, matchRepo, find_dependencies
from lmh.lib.repos.remote import install
from lmh.lib.config import get_config
from lmh.lib.extenv import get_template


from lmh.lib.git import push as git_push
from lmh.lib.git import pull as git_pull
from lmh.lib.git import status as git_status
from lmh.lib.git import commit as git_commit
from lmh.lib.git import do as git_do
from lmh.lib.git import do_data as git_do_data
from lmh.lib.git import root_dir as git_root_dir

#
# Matching Repository names
#

def match_repository(dirname=os.getcwd()):
	"""Matches a folder to the closest repository. """

	t = os.path.realpath(dirname)

	if not t.startswith(data_dir):
		return None

	comp = t[len(data_dir)+1:].split("/")

	if len(comp) < 2:
		return None

	return "/".join(comp[:2])

def match_repositories(args):
	"""Matches a list of repositories to a list of absolute paths"""

	spec = None

	if len(args.repository) == 0:
		spec = [matchRepo(".", data_dir+"/*/*")]
	if args.all:
		spec = [matchRepo(data_dir, data_dir)]
	if spec == None:
		spec = args.repository

	repos = []
	for repol in spec:
		for repo in glob.glob(repol):
			repos.append(repo)
	# TODO: Check if this is a repository
	repos = filter(lambda x:os.path.isdir(x), repos)

	return repos




#
# Local indexers
#

def find_all_locals():
	"""Finds all locally installed repositories"""

	ldirs = []

	# find all sub-sub dirs in the data directory
	for grp in os.listdir(data_dir):
		if os.path.isdir(data_dir + "/" + grp):
			for repo in os.listdir(data_dir + "/" + grp):
				fullPath = data_dir + "/" + grp + "/" + repo
				if os.path.isdir(fullPath) and is_valid_repo(fullPath):
					ldirs.append(grp + "/" + repo)

	return ldirs

#
# Import / Export of all existing repos to a certain file
#

def export(file = None):
	"""Exports the list of currently installed repositories. """

	# Get all locally installed directories
	installed = find_all_locals()

	if(file == None):
		for mod in installed:
			std(mod)
		return True
	try:
		write_file(file, s.linesep.join(things))
		return True
	except:
		err("Unable to write "+fn)
		return False

def restore(file = None):
	"""Restores a list of currently installed repositories. """

	# read all lines from the file
	lines = read_file_lines(file)
	lines = [l.strip() for l in lines]
	return install(*lines)

def push(*repos):
	"""Pushes all currently installed repositories. """

	ret = True

	for rep in repos:
		std("git push", rep)
		ret = git_push(rep) and ret

	return ret

def pull(*repos):
	"""Pulls all currently installed repositories and updates dependencies"""

	ret = True

	for rep in repos:
		std("git pull", rep)

		ret = git_pull(rep) and ret

		rep = match_repository(rep)
		ret = install(rep) and ret

	return ret

def status(*repos):
	"""Does git status on all installed repositories """

	ret = True

	for rep in repos:
		std("git status", rep)
		val = git_status(rep)
		if not val:
			err("Unable to run git status on", rep)
			ret = False
		else:
			std(val)

	return ret

def commit(msg, *repos):
	"""Commits all installed repositories """

	ret = True

	for rep in repos:
		std("git commit", rep)
		ret = git_commit(rep, "-a", "-m", msg) and ret

	return ret

def do(cmd, args, *repos):
	"""Does an arbitraty git commit on all repositories. """
	ret = True
	args = args[0].split(" ")
	for rep in repos:
		std("git "+cmd, " ".join(args), rep)
		ret = git_do(rep, cmd, *args) and ret

	return ret

def clean(repo, args):
	"""Cleans up repositories. """
	return do("clean", ["-f"], repo)

def log(ordered, *repos):
	"""Prints out log messages on all repositories. """
	ret = True

	def get_log(repo):
		get_format = lambda frm:git_do_data(repo, "log", "--pretty=format:"+frm+"")[0].split("\n")

		hash_short = get_format("%h")
		commit_titles = get_format("%s")
		dates = get_format("%at")
		dates_human = get_format("%ad")
		author_names = get_format("%an")
		author_mails = get_format("%ae")

		res = [{
			"hash": hash_short[i],
			"subject": commit_titles[i],
			"date": int(dates[i]),
			"date_human": dates_human[i],
			"author": author_names[i],
			"author_mail": author_mails[i],
			"repo": match_repository(repo)
		} for i in range(len(hash_short))]

		return res

	entries = []

	for rep in repos:
		try:
			entries.extend(get_log(rep))
		except Exception as e:
			err(e)
			ret = False


	if ordered:
		entries.sort(key=lambda e: -e["date"])

	strout = ""

	for entry in entries:
		strout += "\nRepo:    " + entry["repo"]
		strout += "\nSubject: " + entry["subject"]
		strout += "\nHash:    " + entry["hash"]
		strout += "\nAuthor:  " + entry["author"] + " <" + entry["author_mail"] + ">"
		strout += "\nDate:    " + entry["date_human"]
		strout += "\n"

	std_paged(strout, newline=False)

	return ret

def create(dirname = ".", use_git_root = False):
	"""Creates a new repository in the given directory"""


	if use_git_root:
		rootdir = git_root_dir(dirname)
	else:
		rootdir = os.path.abspath(dirname)

	std("Creating new MathHub repository in", rootdir)

	if (not use_git_root and not (not os.listdir(rootdir))) and (not get_config("init::allow_nonempty")):
		err("Could not create repository, directory not empty. ")
		err("If you want to use the root of the current git repository, please use lmh install -g")
		err("If you want to enable lmh init on non-empty directories, please run")
		err("    lmh config init::allow_nonempty true")
		return False

	metadir = rootdir+"/META-INF"

	tManifest = get_template("manifest.tpl")
	tBuild = get_template("build.tpl")
	tServe = get_template("serve.tpl")

	emptyrepo = install_dir + "/bin/emptyrepo"

	try:
		copytree(emptyrepo, rootdir)
	except Exception as e:
		err("Error initalising directory. ")
		err(e)
		return False

	try:
		name = match_repository(rootdir).split("/")
		group = name[0]
		name = name[1]
	except:
		err("Could not detect repository group & name. ")
		return False

	if not os.path.exists(metadir+"/MANIFEST.MF"):
		write_file(metadir+"/MANIFEST.MF", tManifest.format(group, name))

	if not os.path.exists(rootdir+"/build.msl"):
		write_file(rootdir+"/build.msl", tBuild.format(group, name, install_dir))

	if not os.path.exists(rootdir+"/serve.msl"):
		write_file(rootdir+"/serve.msl", tServe.format(group, name, install_dir))

	if not use_git_root:
		if not git_do(rootdir, "init"):
			err("Error creating git repository. ")
			err("The directory has been created successfully, however git init failed. ")
			err("Please run it manually. ")
			return False

	if not (git_do(rootdir, "add", "-A") and git_commit(rootdir, "-m", "Repository created by lmh")):
		err("Error creating inital commit. ")
		err("The directory has been created successfully, however git commit failed. ")
		err("Please run it manually. ")
		return False

	std("""Created new repository successfully.
If the new repository depends on other MathHub repositories, we can add them in the line starting with
"dependencies:" in META-INF/MANIFEST.MF. Note that any changes have to be committed and pushed before
the repository can be used by others. """)
	return True

def replace(replacer, replace_args, fullPath, m):
	std("replacing at %r"%fullPath)
	if replacer == None:
		return m.group(0)
	for idx, g in enumerate(m.groups()):
		replace_args["g"+str(idx)] = g

	res = Template(replacer).substitute(replace_args)

	return res

def replacePath(dirname, matcher, replaceFnc, apply=False):
  try:
    compMatch = re.compile(matcher)
  except Exception as e:
    err("failed to compile matcher %r"%matcher)
    err(e)
    return False

  for root, dirs, files in os.walk(dirname):
    path = root.split('/')
    for file in files:
      fileName, fileExtension = os.path.splitext(file)
      if fileExtension != ".tex":
        continue
      fullpath = root+"/"+file
      if not os.access(fullpath, os.R_OK): # ignoring files I cannot read
        continue
      changes = False
      replaceContext = functools.partial(replaceFnc, fullpath)
      for line in open(fullpath, "r"):
        newLine = compMatch.sub(replaceContext, line)
        if newLine != line:
          changes = True
          std(fullpath + ": \n " + line + newLine)

        if apply:
          write_file(fullpath+".tmp", newLine)
      if apply:
        if changes:
          os.rename(fullpath+".tmp", fullpath)
        else:
          os.remove(fullpath+".tmp")

def find(rep, args):
	"""Finds pattern in repositories"""

	replacer = None
	repname = match_repository(rep)

	matcher = Template(args.matcher).substitute(repo=repname)

	if args.replace:
		replacer = args.replace[0]

	replace_args = {"repo" : repname}

	replaceFnc = functools.partial(replace, replacer, replace_args)

	return replacePath(rep, matcher, replaceFnc, args.apply)


def write_deps(dirname, deps):
	"""Writes dependencies into a given module. """

	f = os.path.join(data_dir, match_repository(dirname), "META-INF", "MANIFEST.MF")
	n = re.sub(r"dependencies: (.*)", "dependencies: "+",".join(deps), read_file(f))
	write_file(f, n)
	std("Wrote new dependencies to", f)


def calc_deps(apply = False, dirname="."):
	"""Crawls for dependencies in a given directory. """

	repo = match_repository(dirname)

	if not repo:
		return False

	std("Checking dependencies for:   ", repo)

	# Getting the real dependencies
	given_dependencies = find_dependencies(match_repository(dirname))+[repo]
	given_dependencies = list(set(given_dependencies))

	# All the required paths
	real_paths = {}

	for root, dirs, files in os.walk(dirname):
		path = root.split('/')
		for file in files:
			fileName, fileExtension = os.path.splitext(file)
			if fileExtension != ".tex":
				continue

			# read the file
			for f in read_file_lines(root+"/"+file):

				for find in re.findall(r"\\(usemhvocab|usemhmodule|adoptmhmodule|importmhmodule)\[(([^\]]*),)?repos=([^,\]]+)(\s*)(,([^\]])*)?\]", f):
					real_paths[find[3]] = True

				for find in re.findall(r"\\(usemodule|adoptmodule|importmodule|usevocab)\[([^\]]+)\]", f):
					real_paths[find[1]] = True

				for find in re.findall(r"\\(MathHub){([^\}]+)}", f):
					real_paths[find[1]] = True

				for find in re.findall(r"\\(gimport|guse|gadpot)\[([^\]]+)\]", f):
					real_paths[find[1]] = True

	# Now only take paths which have exactly two parts
	real_dependencies = []
	for path in real_paths:
		comps = path.split("/")
		if len(comps) < 2:
			continue
		real_dependencies.append(comps[0]+"/"+comps[1])

	real_dependencies = list(set(real_dependencies))

	# No need to require itself
	while repo in real_dependencies: real_dependencies.remove(repo)
	while repo in given_dependencies: given_dependencies.remove(repo)


	# we are missing the ones that are real but not given
	missing = filter(lambda x:not x in given_dependencies, real_dependencies)

	# we do not need those that are given but not real
	not_needed = filter(lambda x:not x in real_dependencies, given_dependencies)

	# the others are fine
	fine  = filter(lambda x:x in real_dependencies, given_dependencies)

	ret = {
		"fine": fine,
		"missing": missing,
		"not_needed": not_needed,
		"should_be": real_dependencies
	}

	std("---")
	if len(ret["fine"]) > 0:
		std(term_colors("green"),  "Used dependencies:         ", term_colors("normal"), ", ".join(ret["fine"]))
	if len(ret["not_needed"]) > 0:
		std(term_colors("yellow"), "Superfluous dependencies:  ", term_colors("normal"), ", ".join(ret["not_needed"]))
	if len(ret["missing"]) > 0:
		std(term_colors("red"),    "Missing dependencies:      ", term_colors("normal"), ", ".join(ret["missing"]))
	std("---")
	if len(ret["missing"]) > 0 or len(ret["not_needed"]) > 0:
		std("Dependencies should be: ", ", ".join(ret["should_be"]))

	if apply:
		write_deps(dirname, ret["should_be"])

	return ret
