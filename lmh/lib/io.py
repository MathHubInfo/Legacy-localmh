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

import sys
import os.path
import shutil

from subprocess import Popen, PIPE, STDOUT

def term_colors(c):
	colors = {
		"grey": "\033[01;30m", 
		"red": "\033[01;31m", 
		"green": "\033[01;32m", 
		"yellow": "\033[01;33m", 
		"blue": "\033[01;34m", 
		"magenta": "\033[01;35m", 
		"cyan": "\033[01;36m", 
		"white": "\033[01;37m", 
		"normal": "\033[00m"
	}

	from lmh.lib.config import get_config

	if get_config("self::enable_colors"):
		return colors[c]
	else:
		return ""


#
# Error & Normal Output
#

# Allow supression of outputs
__supressStd__ = False
__supressErr__ = False

def std(*args, **kwargs):
	"""Prints some values to stdout"""

	newline = True

	# allow only the newline kwarg
	for k in kwargs:
		if k != "newline":
			raise TypeError("std() got an unexpected keyword argument '"+k+"'")
		else:
			newline = kwargs["newline"]

	if not __supressStd__:
		text = " ".join([str(text) for text in args]) + ('\n' if newline else '')
		sys.stdout.write(text)

def err(*args, **kwargs):
	"""Prints some text to stderr"""

	newline = True

	# allow only the newline kwarg
	for k in kwargs:
		if k != "newline":
			raise TypeError("std() got an unexpected keyword argument '"+k+"'")
		else:
			newline = kwargs["newline"]

	if not __supressErr__:
		text = " ".join([str(text) for text in args]) + ('\n' if newline else '')
		sys.stderr.write(term_colors("red")+text+term_colors("normal"))

def std_paged(*args, **kwargs):
	"""Pages output if a pager is available. """

	from lmh.lib.config import get_config

	newline = True

	# allow only the newline kwarg
	for k in kwargs:
		if k != "newline":
			raise TypeError("std() got an unexpected keyword argument '"+k+"'")
		else:
			newline = kwargs["newline"]

	if not __supressStd__:
		pager = get_config("env::pager")

		if pager == "":
			return std(*args, **kwargs)
		try:
			p = Popen([pager], stdout=sys.stdout, stderr=sys.stderr, stdin=PIPE)
			p.communicate(" ".join([str(text) for text in args]) + ('\n' if newline else ''))
		except:
			err("Unable to run configured page. ") 
			err("Please check your value for env::pager. ")
			err("Falling back to STDOUT. ")
			return std(*args, **kwargs)




def read_raw(query = None):
	"""Reads a line of text form stdin. """

	if query != None:
		std(query, newline=False)
	return sys.stdin.readline().strip()

def block_std():
	"""Blocks stdout"""
	__supressStd__ = True

def unblock_std():
	"""Unblocks stdout"""
	__supressStd__ = False

def block_err():
	"""Blocks stderr"""
	__supressErr__ = True

def unblock_err():
	"""Unblocks stderr"""
	__supressErr__ = False

#
# File reading / writing
#

def write_file(filename, text):
	"""Writes text to file"""

	# Write the text to file
	text_file = open(filename, "w")
	text_file.write(text)
	text_file.close()

def read_file(filename):
	"""Reads text from a file"""

	# Read some text and then close the file
	text_file = open(filename, "r")
	text = text_file.read()
	text_file.close()

	return text

def read_file_lines(filename = None):
	"""Reads all text lines from a file"""

	if filename == None:
		return sys.stdin.readlines()

	# Read lines and then close the file
	text_file = open(filename, "r")
	lines = text_file.readlines()
	text_file.close()

	return lines

def copytree(src, dst, symlinks=False, ignore=None):
	"""Replacement for shuitil.copytree"""
	
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)

def effectively_readable(path):
	"""Checks if a path ios effectively readable"""

	uid = os.getuid()
	euid = os.geteuid()
	gid = os.getgid()
	egid = os.getegid()

	# This is probably true most of the time, so just let os.access()
	# handle it.  Avoids potential bugs in the rest of this function.
	if uid == euid and gid == egid:
		return os.access(path, os.R_OK)

	st = os.stat(path)

	# This may be wrong depending on the semantics of your OS.
	# i.e. if the file is -------r--, does the owner have access or not?
	if st.st_uid == euid:
		return st.st_mode & stat.S_IRUSR != 0

	# See comment for UID check above.
	groups = os.getgroups()
	if st.st_gid == egid or st.st_gid in groups:
		return st.st_mode & stat.S_IRGRP != 0