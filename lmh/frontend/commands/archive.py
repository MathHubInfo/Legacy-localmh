from lmh.frontend import command
from lmh.mathhub.resolvers import resolver

class ArchiveCommand(command.Command):
    """
    A command that is iterates over individual archives
    """
    
    def __init__(self, name, local):
        """
        Creates a new ArchiveCommand() instance
        
        Arguments:
            name
                The name of this command
            local
                If set to True will iterate over local archives. If set to False
                will iterate over remote commands. 
        """
        super(ArchiveCommand, self).__init__(name)
        
        self.__local = local
        
    
    def _init_repo_argparse(self, subparsers):
        """
        Function that is called to add initialise a new subparser representing
        this command. May throw NotImplementedError. 
        
        Arguments:
            subparsers
                Argparse subparsers object to add parsers to
        
        Returns: 
            a new SubParser that is to be added 
        """
        
        return subparsers.add_parser(self.name, help=self.__doc__, description=self.__doc__)
    
    def _add_args_argparse(self, command):
        """
        Function that should add arguments to the ArgParse object representing
        this command. 
        
        
        Arguments:
            command
                Argparse object representing this command. 
        """
        
        pass
    
    def _build_argparse(self, subparsers):
        """
        Function that adds a new subparser representing this parser. 
        
        Arguments:
            subparsers
                Argparse subparsers object to add parsers to
        """
        
        parser = self._init_repo_argparse(subparsers)
        
        archives = parser.add_argument_group('Archives')
        archives.add_argument('archives', metavar='archive', nargs='*', help='a list of %s repositories' % ('local' if self.__local else 'remote'))
        archives.add_argument('--all', "-a", default=False, const=True, action="store_const", help="select all repositories")
        archives.add_argument('--instance', "-i", default=None, help="Use only repositories from the selected instance")
        
        self._add_args_argparse(parser)
    
    def call_single(self, archive, *args, parsed_args=None):
        """
        Calls this command with the given arguments on a single archive
        
        Arguments:
            archive
                Archive to run the command over
            *args
                A list of strings passed to this command. In case an argparse 
                object (with the parsed_args) is given, this corresponds to the 
                arguments unknown to argparse. 
            parsed_args
                An argparse object representing the arguments passed to this 
                command. In order to use this properly use self._build_argparse()
        Returns:
            A Boolean indicating if the command was succesfull
        """
        
        raise NotImplementedError
    
    def _join(self, codes):
        """
        Protected function used to turn a list of return codes (one per Archive)
        into a single return code for the function. This defaults to doing a
        logical and over the input
        
        Arguments:
            codes
                a list of return codes from self.call_single()
        Returns:
            a single return code for self.call()
        """
        
        andc = True
        for c in codes:
            andc &= c
        return andc
    
    def call_all(self, archives, *args, parsed_args=None):
        """
        Calls this command for the given archives with the given arguments. If 
        not overriden by subclass simply calls self.call_single()
        
        Arguments:
            archives
                List of LMHArchive() instances to run the command over
            *args
                A list of strings passed to this command. In case an argparse 
                object (with the parsed_args) is given, this corresponds to the 
                arguments unknown to argparse. 
            parsed_args
                An argparse object representing the arguments passed to this 
                command. In order to use this properly use self._build_argparse()
        Returns:
            None, a Boolean or an Integer representing the return code from this 
            command. If the return code is None we assume that the command exited
            normally. 
        """
        
        return self._join([self.call_single(a, *args, parsed_args=parsed_args) for a in archives])
    
    def call(self, *args, parsed_args=None):
        """
        Calls this command with the given arguments. 
        
        Arguments:
            *args
                A list of strings passed to this command. In case an argparse 
                object (with the parsed_args) is given, this corresponds to the 
                arguments unknown to argparse. 
            parsed_args
                An argparse object representing the arguments passed to this 
                command. In order to use this properly use self._build_argparse()
        Returns:
            None, a Boolean or an Integer representing the return code from this 
            command. If the return code is None we assume that the command exited
            normally. 
        """
        
        # take out the repository arguments
        archivestrs = parsed_args.archives
        instance = parsed_args.instance
        has_all = parsed_args.all
        
        del parsed_args.archives
        del parsed_args.instance
        del parsed_args.all
        
        # get the base
        the_base = self.commander.get_base()
        
        # get the resolve command
        resolve_command = self.manager.resolve_local_archives if self.__local else self.manager.resolve_remote_archives
        
        # resolve the archives
        if has_all:
            try:
                archives = resolve_command(base_group = the_base, instance = instance)
            except resolver.GroupNotFound:
                archives = resolve_command(instance = instance)
        else:
            try:
                archives = resolve_command(*archivestrs, base_group = the_base, instance = instance)
            except resolver.GroupNotFound:
                archives = resolve_command(*archivestrs, instance = instance)
        
        return self.call_all(archives, *args, parsed_args=parsed_args)

class LocalArchiveCommand(ArchiveCommand):
    """
    A command that is iterates over individual localarchives
    """
    
    def __init__(self, name):
        """
        Creates a new LocalArchiveCommand() instance
        
        Arguments:
            name
                The name of this command
        """
        super(LocalArchiveCommand, self).__init__(name, True)

class RemoteArchiveCommand(ArchiveCommand):
    """
    A command that is iterates over individual remote archives
    """
    
    def __init__(self, name):
        """
        Creates a new RemoteArchiveCommand() instance
        
        Arguments:
            name
                The name of this command
        """
        super(RemoteArchiveCommand, self).__init__(name, False)