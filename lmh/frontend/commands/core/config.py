from lmh.frontend import command

class ConfigCommand(command.Command):
    """
    View or change lmh configuration
    """
    
    def __init__(self):
        """
        Creates a new ConfigCommand() object. 
        """
        
        super(ConfigCommand, self).__init__('config')
    
    def _build_argparse(self, subparsers):
        """
        Function that should add arguments to the ArgParse object representing
        this command. 
        
        Arguments:
            command
                Argparse object representing this command. 
        """
        
        command = subparsers.add_parser(self.name, help=self.__doc__)
        
        command.add_argument('key', nargs='?', help="Name of setting to change. ", default=None)
        command.add_argument('value', nargs='?', help="New value for setting. If omitted, show some information about the given setting. ", default=None)
        
        command.add_argument('-p', '--porcelain', help="When getting a config setting return only its value ", default=False, action="store_true")
        command.add_argument('--reset', help="Resets a setting. Ignores value. ", default=False, action="store_true")
        #command.add_argument('--reset-all', help="Resets all settings. ", default=False, action="store_const", const=True)
    
    def call(self, parsed_args):
        """
        Calls this command
        
        Arguments:
            parsed_args
                Argparse object representing the parsed settings
        
        Returns:
            None, a Boolean or an Integer representing the return code from this 
            command. If the return code is None we assume that the command exited
            normally. 
        """
        
        if parsed_args.reset:
            if parsed_args.key == None:
                self.manager.logger.fatal('Missing key')
                return False
                
            self.manager('reset-config', parsed_args.key)
            return True

        if parsed_args.key == None:
            
            info = self.manager('get-config-info')
            self.manager.logger.log(info)
            self.manager.logger.log("Type 'lmh config KEY' to get more information on KEY. ")
            self.manager.logger.log("Type 'lmh config KEY VALUE' to change KEY to VALUE. ")
            
            return True
        elif parsed_args.value == None:
            
            info = self.manager('get-config-info', parsed_args.key) if not parsed_args.porcelain else self.manager('get-config', parsed_args.key)
            if info == None:
                return False
            
            self.manager.logger.log(info)
            
            return True
        else:
            try:
                self.manager('set-config', parsed_args.key, parsed_args.value)
                return True
            except KeyError:
                return False