class StandardCommands(object):
    @staticmethod
    def register_to(commander):
        """
        Registers all standard commands to the given Commander() instance. 
        
        Arguments:
            commander
                Commander() to register all standard commands to
        """
        
        from lmh.frontend.commands.core import about, config, root
        
        commander += config.ConfigCommand()
        commander += about.AboutCommand()
        commander += root.RootCommand()
        
        # other commands
        from lmh.frontend.commands.management import dtree, listing, install
        
        commander += install.InstallCommand()
        commander += dtree.DTreeCommand()
        commander += listing.LocalListCommand()
        commander += listing.RemoteListCommand()
        
        # legacy commands
        StandardCommands.register_legacy_commands_to(commander)
        
        # Standard aliases
        StandardCommands.register_standard_aliases_to(commander)
    
    @staticmethod
    def register_standard_aliases_to(commander):
        """
        Registers all standard aliases to the given Commander() instance. 
        
        Arguments:
            commander
                Commander() to register all standard commands to
        """
        
        from lmh.frontend.commands import alias
        
        # Aliases for Status + Commands
        commander += alias.AliasCommand('ci', 'commit')
        commander += alias.AliasCommand('si', 'status')
        
        # selfupdate
        commander += alias.AliasCommand('selfupdate', 'setup', '--update', 'self')
        
        # lmh gen*
        commander += alias.AliasCommand('gen', 'mmt', 'make')
        commander += alias.AliasCommand('sms', 'gen', 'sms')
        commander += alias.AliasCommand('omdoc', 'gen', 'latexml')
        commander += alias.AliasCommand('pdf', 'gen', 'pdflatex')
        commander += alias.AliasCommand('alltex', 'gen', 'alltex')
        commander += alias.AliasCommand('allpdf', 'gen', 'allpdf')
        
        # Depreacted Aliases
        commander += alias.AliasCommand('update', 'pull', depracated = True)
        commander += alias.AliasCommand('ls', 'ls-local', depracated = True)
    @staticmethod
    def register_legacy_commands_to(commander):
        """
        Registers all legacy commands to the given Commander() instance. 
        
        Arguments:
            commander
                Commander() to register all standard commands to
        """
        
        from lmh.utils import fileio
        import json
        
        from lmh.lib.dirs import lmh_locate
        
        lc = json.loads(fileio.read_file(lmh_locate("lmh", "data", "commands.json")))
        
        from lmh.frontend.commands import legacy
        
        for c in lc:
            commander += legacy.LegacyCommand(c)
        
    