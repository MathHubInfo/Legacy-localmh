from lmh.frontend import command
from lmh.mathhub.resolvers import resolver, remote

class ArchiveCommand(command.Command):
    """
    A command that is iterates over individual archives
    """
    
    def __init__(self, name, support_all = True, single = False):
        """
        Creates a new ArchiveCommand() instance
        
        Arguments:
            name
                The name of this command
            support_all
                Optional. Boolean indicating if the action is supported for all archives
                at once by giving an empty list of archives. Default to True. 
            single
                Optional. If set to True require exactly one archive argument. 
                Overwrites support_all. 
        """
        super(ArchiveCommand, self).__init__(name)
        
        self.__support_all = support_all
        self.__single = single
        
    
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
        
        if self.__single:
            archives.add_argument('archives', metavar='archive', nargs=1, help='a single repository')
        elif self.__support_all:
            archives.add_argument('archives', metavar='archive', nargs='*', help='a list of repositories')
            archives.add_argument('--all', "-a", default=False, const=True, action="store_const", help="select all repositories")
        else:
            archives.add_argument('archives', metavar='archive', nargs='+', help='a non-empty list of repositories')
        
        archives.add_argument('--instance', "-g", default=None, help="Use only repositories from the selected instance")
        
        
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
    
    def _resolve(self, *spec, base_group = None, instance = None):
        """
        Protected function used to resolve a list of archives. To be overidden
        by subclass. 
        
        Arguments:
            *spec
                A list of strings, pairs, LMHArchive or patterns containing *s 
                that will be matched against the full names of repositories of 
                the form 'group/name'.
                If empty and base_group is None, the full list of repositories 
                will be returned. If empty and base_group has some value only
                repositories from that group will be returned. 
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group. 
            instance
                Optional. If set returns only repositories from the 
                instance matching the given name. 
        Returns:
            A list of archives
        """
        raise NotImplementedError
    
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
        del parsed_args.archives
        
        instance = parsed_args.instance
        del parsed_args.instance
        
        if self.__single:
            has_all = False
        elif self.__support_all:
            has_all = parsed_args.all
            del parsed_args.all
        else:
            has_all = False
        
        # get the base
        the_base = self.commander.get_base()
        
        # resolve the archives
        if has_all:
            try:
                archives = self._resolve(base_group = the_base, instance = instance)
            except resolver.GroupNotFound:
                archives = self._resolve(instance = instance)
        else:
            try:
                archives = self._resolve(*archivestrs, base_group = the_base, instance = instance)
            except resolver.GroupNotFound:
                archives = self._resolve(*archivestrs, instance = instance)
        
        if archives == None:
            return False
        
        if self.__single:
            if len(archives) != 1:
                self.manager.logger.error('Expected exactly one repository. Please check that the spelling is correct. ')
                return False
            return self.call_single(archives[0], *args, parsed_args=parsed_args)
        return self.call_all(archives, *args, parsed_args=parsed_args)

class LocalArchiveCommand(ArchiveCommand):
    """
    A command that is iterates over individual localarchives
    """
    
    def _resolve(self, *spec, base_group = None, instance = None):
        """
        Protected function used to resolve a list of archives. 
        
        Arguments:
            *spec
                A list of strings, pairs, LMHArchive or patterns containing *s 
                that will be matched against the full names of repositories of 
                the form 'group/name'.
                If empty and base_group is None, the full list of repositories 
                will be returned. If empty and base_group has some value only
                repositories from that group will be returned. 
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group. 
            instance
                Optional. If set returns only repositories from the 
                instance matching the given name. 
        Returns:
            A list of archives
        """
        return self.manager.resolve_local_archives(*spec, base_group = base_group, instance = instance) 

class RemoteArchiveCommand(ArchiveCommand):
    """
    A command that is iterates over individual remote archives
    """
    
    def _resolve(self, *spec, base_group = None, instance = None):
        """
        Protected function used to resolve a list of archives. 
        
        Arguments:
            *spec
                A list of strings, pairs, LMHArchive or patterns containing *s 
                that will be matched against the full names of repositories of 
                the form 'group/name'.
                If empty and base_group is None, the full list of repositories 
                will be returned. If empty and base_group has some value only
                repositories from that group will be returned. 
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group. 
            instance
                Optional. If set returns only repositories from the 
                instance matching the given name. 
        Returns:
            A list of archives or None if resolution failed
        """
        
        try:
            return self.manager.resolve_remote_archives(*spec, base_group = base_group, instance = instance) 
        except remote.NetworkingError:
            self.manager.logger.error('NetworkingError when attempting to resolve remote archives')
            return None
        