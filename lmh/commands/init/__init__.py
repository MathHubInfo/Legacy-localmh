from .. import CommandClass
from . import meta
import argparse

class Command(CommandClass):
    def __init__(self):
        if meta.about:
            self.help = meta.about()
        else:
            self.help = "<No help available>"
    def add_parser_args(self, parser):
        if meta.add_parser_args:
            return meta.add_parser_args(parser, argparse)
        else:
            return parser
    def do(self, arguments, unparsed):
        from . import run
        return run.do(arguments, unparsed)
