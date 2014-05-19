# New module ports

* better doc
* return True or False
* use lmh.lib whenever possible to share all code
* unuse lmh.util

# Still to port the following files:

commands.init
commands.find
commands.gen.* <-- Hardest
commands.checkpaths
commands.clean
commands.depcrawl
commands.mvmod
commands.symbols <-- Not finished
commands.__init__
__init__

# Ported already
commands.about
commands.config
commands.install
commands.mine
commands.shell
commands.selfupdate
commands.setup
commands.push
commands.status
commands.update
commands.git
commands.log

# TODO / New Stuff

* unify repotType and parseRepo
* --version arg to __init__
* lmh symbols
* in the master, preparse lmh git args
* autocomplete
* firstrun code
* add *s to the repository names
* in commands.__init__, regroup commands

# Currently completly unsupported / broken: 

commands.xhtml
.agg
.mmt
.server
