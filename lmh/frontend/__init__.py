# avoid the cyclic import
from lmh.frontend.command import Command
del Command

__all__ = ["commands", "command", "commander", "main", "stamdard_commands"]
