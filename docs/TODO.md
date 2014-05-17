# New module ports

* better doc
* return True or False
* use lmh.lib whenever possible to share all code

# Still to port the following files:

commands.__init__
commands.checkpaths
commands.clean
commands.commit
commands.depcrawl
commands.find
commands.git
commands.init
commands.log
commands.mvmod
commands.push
commands.selfupdate
commands.setup
commands.shell
commands.status
commands.symbols
commands.update
commands.gen.*

# Ported already

commands.about
commands.config
commands.install
commands.mine

# Currently completly unsupported / broken: 

commands.xhtml
.agg
.mmt
.server
.util

# Existing "new" structure
lmh.__init__ => (Empty)

lmh.commands.__init__ => General command setup
lmh.commands.$COMMAND => Code for $COMMAND

lmh.lib.__init__
lmh.lib.config => Config managing
lmh.lib.env => Installation environment
lmh.lib.io => Input / Output management
lmh.lib.repos.__init__
lmh.lib.repos.local => Manage lcoally installed repositories
lmh.lib.repos.remote => Install remote repositories and check if they exist