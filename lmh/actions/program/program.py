from lmh.actions import action

class ProgrammableAction(action.Action):
    """
    An Action that wraps a Program
    """
    
    def run(self):
        """
        Returns the wrapped program instance
        
        Returns: 
            The program instance
        """
        
        return self._program