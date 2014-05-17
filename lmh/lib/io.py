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
		sys.stderr.write(text)

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