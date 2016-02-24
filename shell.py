"""
This file is the main entry point for lmh. 

To use it properly, run:
python3 shell.py [arguments]
"""

from lmh.frontend import main
main.LMHMain.main(*sys.argv[1:])