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
import distutils.dir_util
from string import Template

from lmh.lib import mkdir_p
from lmh.lib.env import install_dir
from lmh.lib.io import read_file, write_file, find_files, find_all_files, std, err, read_raw
from lmh.lib.env import data_dir
from lmh.lib.config import get_config
from lmh.lib.repos.local import is_repo_dir
from lmh.lib.repos.remote import find_source
from lmh.lib.repos import is_installed

# Git stuffs
from lmh.lib.git import do as git_do
from lmh.lib.git import root_dir as git_root
from lmh.lib.git import push as git_push
from lmh.lib.git import commit as git_commit

try:
    import gitlab
except:
    err("Missing pyapi-gitlab, please install it. ")
    err("You may want to: ")
    err("   pip install pyapi-gitlab")
    err("or")
    err("   pip install lmh --upgrade")
    err("Some things may not be available and fail miserably. ")
    err("See https://github.com/Itxaka/pyapi-gitlab")
    gitlab = False

# Create the local repository
emptyrepo_dir = os.path.join(install_dir, "bin", "emptyrepo")

def find_types():
    return [name for name in os.listdir(emptyrepo_dir) if os.path.isdir(os.path.join(emptyrepo_dir, name)) and name != "none"]

def copy_template_dir(source, destination, vars):
    """Copies over a template directory. """

    # Make absolute paths
    source = os.path.abspath(source)
    destination = os.path.abspath(destination)

    try:
        # Remove already existing files.
        distutils.dir_util.copy_tree(source, destination)

        # Find all the template files
        for f in find_files(destination, "tpl")[0]:
            # Substitute everything in the template
            newcontent = Template(read_file(f)).safe_substitute(vars)
            write_file(f[:-len(".tpl")], newcontent)
            # Delete the tpl file
            os.remove(f)
    except Exception as e:
        err("Error initalising template. ")
        err(e)
        return False

    return True

def create_remote(group, name):
    """Create a remote repository interactively. """

    if gitlab == False:
        err("Missing pyapi-gitlab, unable to create remote repository. ")
        return False

    remote_host = get_config("gl::host")
    std("Attempting to create repository", remote_host+group+"/"+name)

    # Get the private token
    token = get_config("gl::private_token")

    try:
        if token != "":
            gl = gitlab.Gitlab(remote_host, token=token)
            username = gl.currentuser()["username"]
        else:
            gl = gitlab.Gitlab(remote_host)
            raise Exception
    except:
        std("Unable to login with private token. ")
        std("To use it, please run")
        std("   lmh config gl::private_token <token>")
        std("Your private token can be found under Profile -> Account -> Private token")
        std("Switching to username / password authentication. ")

        username = read_raw("Username for "+remote_host+":")
        password = read_raw("Password for "+username+":", True)

        try:
            if not gl.login(username, password):
                raise Exception
        except:
            err("Gitlab Username/Password Authentication failed. ")
            return False

    std("Authentication successfull, creating project. ")

    # Find group Id
    try:
        gid = None
        if group == username:
            gid = ""
        for g in gl.getgroups():
            if g["path"] == group:
                gid = g["id"]
                break

        if gid == None:
            raise Exception

    except:
        err("Unable to determine group id, make sure")
        err("you have access to the group "+group)
        return False

    # Create the project on the given id
    try:
        p = gl.createproject(name, gid, description="lmh auto-created project "+group+"/"+name, public=1)
        if not p:
            raise Exception


        res = find_source(p["path_with_namespace"], quiet=True)
        if not res:
            return res
        else:
            # Fallback to ssh url
            return p["ssh_url_to_repo"]
    except:
        err("Project creation failed. ")
        return False

    return False

def create(reponame, type="none", remote = True):
    """Creates a new repository in the given directory"""

    # Match the repo name
    absrepo = os.path.abspath(reponame)

    if not is_repo_dir(absrepo, False):
        absrepo = os.path.join(data_dir, reponame)
        if not is_repo_dir(absrepo, False):
            err("Can not resolve repository to create. ")
            return False

    # Figure out the local name
    repo = os.path.relpath(absrepo, data_dir)
    repo_group = repo.split("/")[0]
    repo_name = repo.split("/")[1]

    # Check if it is already installed.
    if is_installed(repo):
        err("Repository", repo, "already installed. ")
        err("Do you maybe want to push this to the remote?")
        return False

    # Make the directory if it does not yet exist.
    try:
        mkdir_p(absrepo)
    except:
        err("Can not create repository directory, unable to create it. ")
        return False

    if not get_config("init::allow_nonempty"):
        if not (not os.listdir(absrepo)):
            err("Target Directory is non-empty. ")
            err("If you want to enable lmh init on non-empty directories, please run")
            err("    lmh config init::allow_nonempty true")
            return False

    # Template Variables.
    tpl_vars = {
            "repo": repo,
            "repo_group": repo_group,
            "repo_name": repo_name,
            "install_dir": install_dir
    }

    # Copy the base template
    if not copy_template_dir(os.path.join(emptyrepo_dir, "none"), absrepo, tpl_vars):
        err("Unable to create repository base. ")
        return False

    # Copy the specific type.
    if type != "none":
        type_dir = os.path.join(emptyrepo_dir, type)
        if os.path.isdir(type_dir):
            if not copy_template_dir(type_dir, absrepo, tpl_vars):
                err("Unable to use repository template. ")
                return False
        else:
            err("Unknown repository type: ", type)
            return False

    if git_root(absrepo) != absrepo:
        # Now lets make an init
        if not git_do(absrepo, "init"):
            err("Error creating git repository. ")
            err("The directory has been created successfully, however git init failed. ")
            err("Please run it manually. ")
            return False

    # Create the initial commit.
    if not (git_do(absrepo, "add", "-A") and git_commit(absrepo, "-m", "Repository created by lmh")):
        err("Error creating inital commit. ")
        err("The directory has been created successfully, however git commit failed. ")
        err("Please run it manually. ")
        return False

    # Can we find a remote for this?
    source = find_source(repo, quiet=True)

    # Don't do anything remote => we are done.
    if not remote:
        if source:
            if not git_do(absrepo, "remote", "add", "origin", source):
                err("Can not add origin. ")
                err("git is suddenly weird. ")
                return False
        else:
            std("Skipping remote creation because --no-remote is given. ")
        std("Repository created successfully. ")
        return True

    # Source does not exist => we will have to create it.
    if not source:
        source = create_remote(repo_group, repo_name)
        if not source:
            err("local repository created but remote creation failed. ")
            return False

    # Add the origin.
    if not git_do(absrepo, "remote", "add", "origin", source):
        err("Can not add origin. ")
        err("git is suddenly weird. ")
        return False

    if not git_push(absrepo, "-u", "origin", "master"):
        err("Repository created but could not push created repository. ")
        err("Check your network connection and try again using git push. ")
        return False

    std("Created new repository successfully. ")

    return True
