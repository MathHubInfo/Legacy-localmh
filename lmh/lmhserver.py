#!/usr/bin/env python

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

import time
import sys
import os
import stomp
import json
import lmh
import cStringIO
import shlex
import threading
import contextlib

user = os.getenv("APOLLO_USER") or "admin"
password = os.getenv("APOLLO_PASSWORD") or "password"
host = os.getenv("APOLLO_HOST") or "localhost"
port = os.getenv("APOLLO_PORT") or 61613
destination = sys.argv[1:2] or ["/queue/lmh_exec"]
destination = destination[0]

@contextlib.contextmanager
def stdout_redirect(where):
  sys.stdout = where
  try:
    yield where
  finally:
    sys.stdout = sys.__stdout__

class MyListener(object):
  
  def __init__(self, conn):
    self.conn = conn
    self.count = 0
    self.start = time.time()
  
  def on_error(self, headers, message):
    print('received an error %s' % message)

  def exec_lmh(self, headers, message):
    if not "reply-to" in headers:
      return
    result = {};
    p = shlex.split(message)[1:]
    new_stdout = cStringIO.StringIO()
    try:
      with stdout_redirect(new_stdout):
        lmh.main(p)
    except Exception, e:
      print "exception", e
      result["err"] = str(e)
    finally:
      if "reply-to" in headers:
        result["out"] = new_stdout.getvalue()
        self.conn.send(headers["reply-to"], json.dumps(result))

  def on_message(self, headers, message):
    try:
      t = threading.Thread(target=self.exec_lmh, args = (headers, message))
      t.daemon = True
      t.start()
    except Exception, e:
      print e

conn = stomp.Connection(host_and_ports = [(host, port)])
conn.set_listener('', MyListener(conn))
conn.start()
conn.connect(login=user,passcode=password)
conn.subscribe(destination=destination, id=0, ack='auto')

print("Waiting for messages...")
time.sleep(100)
print "ending"