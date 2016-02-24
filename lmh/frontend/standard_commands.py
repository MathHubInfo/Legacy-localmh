class StandardCommands(object):
    @staticmethod
    def register_to(commander):
        """
        Registers all standard commands to the given Commander() instance. 
        
        Arguments:
            commander
                Commander() to register all standard commands to
        """
        
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
        commander.add_command(alias.AliasCommand('ci', 'commit'))
        commander.add_command(alias.AliasCommand('si', 'status'))
        
        # update
        commander.add_command(alias.AliasCommand('update', 'pull', depracated = True))
        
        # selfupdate
        commander.add_command(alias.AliasCommand('selfupdate', 'setup', '--update', 'self'))
        
        # lmh gen*
        commander.add_command(alias.AliasCommand('gen', 'mmt', 'make'))
        commander.add_command(alias.AliasCommand('sms', 'gen', 'sms'))
        commander.add_command(alias.AliasCommand('omdoc', 'gen', 'latexml'))
        commander.add_command(alias.AliasCommand('pdf', 'gen', 'pdflatex'))
        commander.add_command(alias.AliasCommand('alltex', 'gen', 'alltex'))
        commander.add_command(alias.AliasCommand('allpdf', 'gen', 'allpdf'))
    
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
            commander.add_command(legacy.LegacyCommand(c))
        
    