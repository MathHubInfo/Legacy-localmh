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
import difflib
import argparse
import functools

from lmh.lib.io import std, err, read_raw
from lmh.lib.env import data_dir
from lmh.lib.modules import makeIndex
from lmh.lib.repos.local import replacePath

fileIndex = {}
remChoices = {}

def replaceFnc(args, fullPath, m):
	if os.path.exists(data_dir+"/"+m.group(1)+".tex"):  # link is ok
		return m.group(0);

	if args.interactive:
		std("Following path is invalid ")

	std(fullPath, ": ", m.group(1))

	if not args.interactive:
		return m.group(0)

	if m.group(0) in remChoices:
		std("Remembered replacement to "+remChoices[m.group(0)])
		return remChoices[m.group(0)];

	comps = m.group(1).split("/");
	fileName = comps[len(comps)-1]+".tex";
	if not fileName in fileIndex:
		err("Error: No suitable index file found "+fileName)
		return m.group(0);

	results = [];
	for validPath in fileIndex[fileName]:
		cnt = 0;
		s = difflib.SequenceMatcher(None, validPath, m.group(1))
		results.append((s.ratio(), validPath));

	results = sorted(results, key=lambda result: result[0], reverse=True)

	std("Possible results: ")
	std("1 ) Don't change")

	for idx, result in enumerate(results):
		std(idx+2,")",result[1])

	while True:
		choice = read_raw('Enter your input:')
		try:
			choice = int(choice)
		except ValueError:
			err("invalid choice")
			continue
		if choice < 1 or choice > len(results) + 1:
			err("Not valid choice")
		break

	while True:
		remember = read_raw('Remember choice (y/n)?:')
		if remember == 'y' or remember == "n":
			break
		err("invalid choice")

	result = m.group(0);

	if choice > 1:
		rPath = results[choice - 2][1][:-4];
		result = "MathHub{"+rPath+"}";

	if remember == 'y':
		remChoices[m.group(0)] = result;

	return result

def checkpaths(dir, args):
	# TODO: UnHardcode the MathHub subdir somehow
	replacePath(dir, r"\\MathHub{([^}]*)", functools.partial(replaceFnc, args), True)

def init():
	fileIndex = makeIndex(data_dir)
	remChoices = {}