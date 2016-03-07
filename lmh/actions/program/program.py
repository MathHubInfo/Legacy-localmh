from lmh.actions import action

class ProgrammableAction(action.Action):
    """
    An Action that wraps a Program
    """
    
    def _set_program(self, pcls, *args, **kwargs):
        """
        Protected function to set the program instance
        
        Arguments:
            pcls
                Class of Program to use
            *args
                Arguments to give to the program
            **kwargs
                Keyword Arguments to give to the program
        """
        
        self.__program = pcls(
            self.manager('locate', 'systems'),
            self.manager('locate', 'sty'), 
            *args, 
            **kwargs
        )
    
    def run(self):
        """
        Returns the wrapped program instance
        
        Returns: 
            The program instance
        """
        try:
            return self.__program
        except AttributeError:
            return None