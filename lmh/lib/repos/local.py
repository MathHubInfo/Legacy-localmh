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
import os.path
import glob

from lmh.lib.env import install_dir, data_dir
from lmh.lib.io import std, std_paged, err, copytree, write_file, read_file_lines
from lmh.lib.repos import is_valid_repo, matchRepo
from lmh.lib.repos.remote import install
from lmh.lib.config import get_config
from lmh.lib.self import get_template


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

def match_repository(dir=os.getcwd()):
	"""Matches a folder to the closest repository. """

	t = os.path.realpath(dir)

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

def export(file):
	"""Exports the list of currently installed repositories. """

	# Get all locally installed directories
	installed = find_all_locals()

	try:
		write_file(file, s.linesep.join(things))
		return True
	except:
		err("Unable to read "+fn)
		return False

def restore(file):
	"""Restores a list of currently installed repositories. """

	# read all lines from the file
	lines = read_file_lines()

	ns = argparse.Namespace()
	ns.__dict__.update({"repository":lines})

	return install.do(ns)

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

def do(cmd, *repos):
	"""Does an arbitraty git commit on all repositories. """

	ret = True

	for rep in repos:
		std("git "+cmd, rep)
		ret = git_do(rep, cmd) and ret

	return ret

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
			print e
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

def create(dir = ".", use_git_root = False):
	"""Creates a new repository in the given directory"""


	if use_git_root:
		rootdir = git_root_dir(dir)
	else:
		rootdir = os.path.abspath(dir)

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