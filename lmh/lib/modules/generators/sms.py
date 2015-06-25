from . import Generator
from lmh.lib import shellquote
from lmh.lib.io import std, read_file_lines
from lmh.lib.modules import needsRegen

import re

ignore = re.compile(r'\\verb')
regStrings = [r'\\(guse|gadopt|symdef|abbrdef|symvariant|keydef|listkeydef|importmodule|gimport|adoptmodule|importmhmodule|adoptmhmodule)', r'\\begin{(module|importmodulevia|importmhmodulevia)}', r'\\end{(module|importmodulevia|importmhmodulevia)}']
regs = map(re.compile, regStrings)

class generate(Generator):
    def __init__(self, quiet, **config):
        self.supportsMoreThanOneWorker = True
        self.prefix = "SMS"
    def needs_file(self, module, gen_mode, text=None):
        if module["type"] != "file":
            return False
        # No sms for localpaths.tex, all.tex and all.*.tex
        if module["mod"] == "localpaths" or module["mod"] == "all" or module["mod"].startswith("all."):
          return False
        if gen_mode == "force" or gen_mode == "update_log" or gen_mode == "grep_log":
            return True
        else:
            return needsRegen(module["path"], module["sms"])

        return False
    def make_job(self, module):
        return module["file"], module["sms"]

    def run_job(self,job,worker_id):
        (input, out) = job

        output = open(out, "w")

        for line in read_file_lines(input):
            idx = line.find("%")
            if idx == -1:
                line = line[0:idx];

            if ignore.search(line):
                continue

            for reg in regs:
                if reg.search(line):
                    text = line.strip()+"%\n"
                    output.write(text)
                    break

        output.close()
        return True
    def dump_job(self, job):
        (input, out) = job

        std("# generate ", out)
        std("echo -n '' > "+shellquote(out))

        for line in open(input):
            idx = line.find("%")
            if idx == -1:
                line = line[0:idx];

            if ignore.search(line):
                continue

            for reg in regs:
                if reg.search(line):
                    text = line.strip()+"%\n"
                    std("echo -n "+shellquote(text)+" >> "+shellquote(out))

        return True
    def get_log_name(self, m):
        return m["sms"]
