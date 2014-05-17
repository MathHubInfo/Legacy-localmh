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

import ConfigParser
import os.path
import json

from lmh.lib.env import install_dir
from lmh.lib.io import std, err, read_file, write_file

"""Available configuration values. """
config_meta = {
	
	#
	# General
	#
	"self::enable_colors": {
		"type": "bool", 
		"help": "Use colors in the output. ",
		"default": False 
	}, 

	"self::git": {
		"type": "string", 
		"help": "Path to the Git executable. Auto-detected if empty. ",
		"default": "" 
	}, 

	# Install Config
	"install::sources": {
		"type": "string", 
		"help": "Url prefixes to clone git repositories from. Seperated by ;s. ", 
		"default": "git@gl.mathhub.info:;http://gl.mathhub.info/", 
	}, 
	"install::nomanifest": {
		"type": "bool", 
		"help": "Allow repositories to install without manifests. ", 
		"default": False
	}, 

	# Sources configuration

	#Latexml
	"setup::latexml::source": {
		"type": "string", 
		"help": "Default Source for latexml. ", 
		"default": "https://github.com/KWARC/LaTeXML.git"
	}, 
	"setup::latexml::branch": {
		"type": "string", 
		"help": "Default branch for latexml. Automatically uses the remote HEAD if undefined. ", 
		"default": ""
	}, 

	#Latexmls
	"setup::latexmls::source": {
		"type": "string", 
		"help": "Default Source for latexmls. ", 
		"default": "https://github.com/dginev/LaTeXML-Plugin-latexmls"
	}, 
	"setup::latexmls::branch": {
		"type": "string", 
		"help": "Default branch for latexmls. Automatically uses the remote HEAD if undefined. ", 
		"default": ""
	}, 

	#STeX
	"setup::stex::source": {
		"type": "string", 
		"help": "Default Source for sTeX. ", 
		"default": "https://github.com/KWARC/sTeX.git"
	}, 
	"setup::stex::branch": {
		"type": "string", 
		"help": "Default branch for sTeX. Automatically uses the remote HEAD if undefined. ", 
		"default": ""
	}, 

	# MMT
	"setup::mmt::source": {
		"type": "string", 
		"help": "Default Source for MMT. ", 
		"default": "https://svn.kwarc.info/repos/MMT/deploy/"
	}, 
	"setup::mmt::branch": {
		"type": "string", 
		"help": "Default branch for MMT. Automatically uses TRUNK if empty. ", 
		"default": ""
	}, 

	# Gitlab settings
	"gl::private_token": {
		"type": "string", 
		"help": "Gitlab Private token for gitlab interaction. Unused. ", 
		"default": "", 
	},
	"gl::host": {
		"type": "string", 
		"help": "Host for gitlab interaction. Unused. ", 
		"default": "http://gl.mathub.info"
	},

	# Init
	"init::allow_nonempty": {
		"type": "bool", 
		"help": "Allow to run lmh init in non-empty directories. ", 
		"default": False
	}, 

	# Generation options
	"gen::default_workers": {
		"type": "int+", 
		"help": "Default number of workers to use for generating pdf and omdoc. ", 
		"default": 8
	}, 

	# Updating options
	"update::selfupdate": {
		"type": "bool", 
		"help": "When lmh update is called without arguments, also perform a selfupdate. ", 
		"default": True
	},

	# Enable some eastereggs
	"::eastereggs": {
		"type": "bool", 
		"help": "Enable some eastereggs. ", 
		"default": False, 
		"hidden": True
	}
}


"""The configuration file for lmh"""
config_file = install_dir + "/bin/lmh.cfg"

def get_config(key):
	"""Gets a given configuration setting. """

	# check if the given key exists
	if not key in config_meta:
		err("Option", key, "does not exist. ")
		raise KeyError

	# Try to find the setting in the config file
	try:
		data = json.loads(read_file(config_file))

		return data[key]
	except:
		pass

	# return the default value
	return config_meta[key]["default"]

def set_config(key, value):
	"""Sets a given configuration setting. """

	# check if the given key exists
	if not key in config_meta:
		err("Option", key, "does not exist. ")
		return False

	# Turn the datatype into whatever we need
	datatype = config_meta[key]["type"]
	if datatype == "string":
		value = str(value)
	elif datatype == "bool":
		value = value.lower()
		if value == "true" or value == "1" or value == "on":
			value = True
		elif value == "false" or value == "0" or value == "off":
			value = False
		else:
			err("Option", key, " is of type boolean, please use the values 'true' or 'false'. ")
			return False
	elif datatype == "int":
		try:
			value = int(value)
		except:
			err("Option", key, " is of type integer, please use a valid integer. ")
			return False
	elif datatype == "int+":
		try:
			value = int(value)
			if value < 0:
				raise ValueError
		except:
			err("Option", key, " is of type positive integer, please use a valid positive integer. ")
			return False

	# Load existsing data
	data = {}	
	try:   
		data = json.load(read_file(config_file))
	except:
		pass

	data[key] = value

	# dump all the content into the file
	try:
		write_file(config_file, json.dumps(data, indent=4))
	except:
		err("Unable to write to config file. ")
		return False

	return True

def reset_config(key):
	""" Resets a given config setting.  """

	# check if the given key exists
	if not key in config_meta:
		err("Option", key, " does not exist, unable to reset. ")
		return False

	set_config(key, str(config_meta[key]["default"]))

def get_config_help(key):
	"""Prints some help about a given config setting. """

	if not key in config_meta:
		err("Option", key, " does not exist. ")
		return False


	meta = config_meta[key]

	std("<" + meta["type"] + "> "+key)
	std(meta["help"])
	std("Current Value: " + json.dumps(get_config(key)))
	std("Default Value: " + json.dumps(meta["default"]))

def list_config():
	"""	Lists available config settings. """

	for key in sorted(config_meta.keys()):
		try:
			if config_meta[key]["hidden"]:
				continue
		except:
			pass
		std(key +" = <" + config_meta[key]["type"] + "> " + json.dumps(get_config(key)))