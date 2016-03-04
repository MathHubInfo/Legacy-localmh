"""
This file is meant for interactive lmh use 
(for debugging purposes by the developer[s])

To use it properly, run:
python3 -i interactive.py
"""

from lmh.frontend import main

commander = main.LMHMain.make_commander()
manager = commander.manager
config = manager.config
mh_manager = manager.mathhub
sys_manager = manager.systems