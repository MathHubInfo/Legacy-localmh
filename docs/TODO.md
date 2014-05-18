# New module ports

* better doc
* return True or False
* use lmh.lib whenever possible to share all code
* unuse lmh.util

# Still to port the following files:
__init__
commands.__init__
commands.checkpaths
commands.clean
commands.depcrawl
commands.find
commands.init
commands.log
commands.mvmod
commands.symbols <-- Not finished
commands.gen.* <-- Hardest


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

# Currently completly unsupported / broken: 

commands.xhtml
.agg
.mmt
.server


# New Stuff

* lmh symbols
* in the master, preparse lmh git args
* autocomplete
* firstrun code
* add *s to the repository names
* in commands.__init__, regroup commands