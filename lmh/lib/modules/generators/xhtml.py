from . import Generator

from lmh.lib.io import std
#from lmh.lib.mmt import compile, compile_dump

class generate(Generator):
    def __init__(self, quiet, **config):
        self.supportsMoreThanOneWorker = True
        self.quiet = quiet
        self.prefix = "XHTML"
    def needs_file(self, module, gen_mode, text=None):
        if module["type"] != "file":
            return False
        else:
            return True
    def make_job(self, module):
        return (module["repo_name"], module["local_uri"])

    def run_job(self,job,worker_id):
        (repo, fpath) = job
        return compile(repo, fpath)
    def dump_init(self):
        std("# XHTML Generation")
        return True
    def dump_job(self, job):
        (repo, fpath) = job
        return compile_dump(repo, fpath)
    def get_log_name(self, m):
        return m["xhtml"]
