from . import Generator
from lmh.lib import shellquote
from lmh.lib.io import std, err, read_file_lines

import re

ignore = re.compile(r'\\verb')
regStrings = [r'\\(guse|gadopt|symdef|abbrdef|symvariant|keydef|listkeydef|importmodule|gimport|adoptmodule|importmhmodule|adoptmhmodule)', r'\\begin{(module|importmodulevia|importmhmodulevia)}', r'\\end{(module|importmodulevia|importmhmodulevia)}']
regs = map(re.compile, regStrings)

class generate(Generator):
    def __init__(self, quiet, **config):
        self.supportsMoreThanOneWorker = True # Do we allow more than one worker?
        self.prefix = "SMS"
    def needs_file(self,module, gen_mode):
        if module["type"] != "file":
            return False
        if gen_mode == "force" or gen_mode == "update_log":
            return True
        elif module["file_time"] > module["sms_time"]:
            return True
        else:
            return False
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
