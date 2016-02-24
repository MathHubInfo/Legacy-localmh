from lmh.frontend.commands import archive

class DTreeCommand(archive.LocalArchiveCommand):
    """
    Shows the depdendency tree of local repositories
    """
    
    def __init__(self):
        """
        Creates a new DTreeCommand() object. 
        """
        
        super(DTreeCommand, self).__init__('deps-tree')
    
    def _add_args_argparse(self, command):
        """
        Function that should add arguments to the ArgParse object representing
        this command. 
        
        
        Arguments:
            command
                Argparse object representing this command. 
        """
        
        
        shallow = command.add_argument_group('Tree expansion').add_mutually_exclusive_group()
        shallow.add_argument('--shallow', dest='shallow', action='store_true', default=True, help='Generate a shallow tree by using a breadth-first approach. Default. ')
        shallow.add_argument('--deep', dest='shallow', action='store_false', help='Generate a fully expanded tree')
        
        sort = command.add_argument_group('Node sorting').add_mutually_exclusive_group()
        sort.add_argument('--sort', dest='sort', action='store_true', default=True, help='Sort dependencies alphabetically and by type. Default. ')
        sort.add_argument('--no-sort', dest='sort', action='store_false', help='Do not sort dependencies')
        
        
        sumnodes = command.add_argument_group('Summarising nodes')
        
        sumunex = sumnodes.add_mutually_exclusive_group()
        sumunex.add_argument('--summarize-unexpanded-nodes', dest='sumunex', action='store_true', default=True, help='Summarise (group together) unexpanded nodes. Default')
        sumunex.add_argument('--keep--unexpanded-nodes', dest='sumunex', action='store_false', help='Do not group unexpanded nodes')
        
        sumcirc = sumnodes.add_mutually_exclusive_group()
        sumcirc.add_argument('--keep-circular-nodes', dest='sumcirc', action='store_false', default=False, help='Do not group circular nodes. Default')
        sumcirc.add_argument('--summarize-circular-nodes', dest='sumcirc', action='store_true', help='Summarise (group together) circular nodes')
    
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
        
        self.manager['print-deps-tree'].run_single(archive, 
            shallow = parsed_args.shallow, 
            sort_nodes = parsed_args.sort, 
            summarize_unexpanded_nodes = parsed_args.sumunex, 
            summarize_circular_nodes = parsed_args.sumcirc
        )
        return True