from .. import CommandClass
from . import meta
import argparse

class Command(CommandClass):
    def __init__(self):
        if meta.about:
            self.help = meta.about()
        else:
            self.help = "<No help available>"

        if hasattr(meta, "allow_unknown_args"):
            self.allow_unknown = meta.allow_unknown_args
        else:
            self.allow_unknown = False

    def add_parser_args(self, parser):
        if meta.add_parser_args:
            return meta.add_parser_args(parser, argparse)
    def do(self, arguments, unparsed):
        from . import run
        return run.do(arguments, unparsed)
