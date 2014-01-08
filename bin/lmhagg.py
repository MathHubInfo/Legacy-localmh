"""
This is a utility library dealing with logging errors and presenting 
them in a user friendly manner

"""

"""
.. py:function:: log_error()

  Logs an error. Tags - a string or a list of string allowing the user to filter errors of certain type.

"""

events = [];

def print_summary():
  print "---------------------- LMH Summary ---------------------";
  errors = 0;

  files = {};
  for ev in events:
    if not ev["file"] in files:
      files[ev["file"]] = [];
    files[ev["file"]].append(ev);

  for file, events in files.items():
    print file
    print events
    for ev in events:
      print ev
      if ev["type"] == "error":
        print "%s:\n%s"%(ev["file"], ev["msg"])

def log_error(tags, file, msg):
  events.append({"type": "error", "tags": tags, "file" : file, "msg": msg})
  pass

def warn_count(tags, file, count):
  events.append({"type": "#warn", "tags": tags, "file" : file, "cnt": count})  
  pass

def error_count(tags, file, count):
  events.append({"type": "#error", "tags": tags, "file" : file, "cnt": count})
  pass