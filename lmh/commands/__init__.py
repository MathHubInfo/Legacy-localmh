#!/usr/bin/env python

from lmh.lib.io import err

class CommandClass():
    def __init__(self):
        self.help = "<No help available for this command>"
    def add_parser_args(self, parser):
        pass
    def do(self, arguments, unparsed):
        pass