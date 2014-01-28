#!/usr/bin/env python

"""
This is a utility library dealing with logging errors and presenting 
them in a user friendly manner

"""

"""
.. py:function:: log_error()

  Logs an error. Tags - a string or a list of string allowing the user to filter errors of certain type.

"""

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

events = [];

def print_summary():
  print "---------------------- LMH Summary ---------------------";
  errors = 0;

  files = {};
  for ev in events:
    if not ev["file"] in files:
      files[ev["file"]] = [];
    if ev["type"] == "error":
      errors = errors + 1
    files[ev["file"]].append(ev);

  print "Errors = %d"%errors
  for file, fileEv in files.iteritems():
    print "%s:"%file
    for ev in fileEv:
      if ev["type"] == "error":
        print "%s"%ev["msg"]

def log_error(tags, file, msg):
  events.append({"type": "error", "tags": tags, "file" : file, "msg": msg})
  pass

def warn_count(tags, file, count):
  events.append({"type": "#warn", "tags": tags, "file" : file, "cnt": count})  
  pass

def error_count(tags, file, count):
  events.append({"type": "#error", "tags": tags, "file" : file, "cnt": count})
  pass