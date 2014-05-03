import ConfigParser

import os.path
import json

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

# Config for the config
config_meta = {

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

	# Untested
	#"untested::enable": {
	#	"type": "bool", 
	#	"help": "Enable untested features. ", 
	#	"default": False
	#},
}

config_file = os.path.dirname(os.path.realpath(__file__)) + "/../bin/lmh.cfg"

def get_config(key):

	# check if the given key exists
	if not key in config_meta:
		print "Option '" + key + "' does not exist. "
		raise KeyError

	# Try to find the setting in the config file
	try:
		with open(config_file) as data_file:    
			data = json.load(data_file)

		return data[key]
	except:
		pass

	# return the default value
	return config_meta[key]["default"]

def set_config(key, value):

	# check if the given key exists
	if not key in config_meta:
		print "Option '" + key + "' does not exist. "
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
			print "Option '" + key + "' is of type boolean, please use the values 'true' or 'false'. "
			return False
	elif datatype == "int":
		try:
			value = int(value)
		except:
			print "Option '" + key + "' is of type integer, please use a valid integer. "
			return False
	elif datatype == "int+":
		try:
			value = int(value)
			if value < 0:
				raise ValueError
		except:
			print "Option '" + key + "' is of type positive integer, please use a valid positive integer. "
			return False

	# Load existsing data
	data = {}	
	try:
		with open(config_file, "r") as data_file:    
			data = json.load(data_file)
	except:
		pass

	data[key] = value

	# dump all the content into the file
	try:
		f = open(config_file, "w")
		f.write(json.dumps(data, indent=4))
		f.close()
	except:
		print "Unable to write to config file. "
		return False

	return True

def reset_config(key):
	# check if the given key exists
	if not key in config_meta:
		print "Option '" + key + "' does not exist, unable to reset. "
		return False

	set_config(key, str(config_meta[key]["default"]))

def get_config_help(key):

	if not key in config_meta:
		print "Option '" + key + "' does not exist. "
		return False


	meta = config_meta[key]

	print "<" + meta["type"] + "> "+key
	print meta["help"]
	print "Current Value: " + json.dumps(get_config(key))
	print "Default Value: " + json.dumps(meta["default"])

def list_config():
	for key in sorted(config_meta.keys()):
		print key +" = <" + config_meta[key]["type"] + "> " + json.dumps(get_config(key)) + ""