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