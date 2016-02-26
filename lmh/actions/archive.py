from lmh.actions import action

class ArchiveBasedAction(action.Action):
    """
    Common Base Class for ArchiveBasedActions. 
    """
    
    def run_single(self, archive, *args, **kwargs):
        """
        Runs this action on a single archive. Needs to be implemented
        by subclass. 
        
        Arguments:
            archive
                LMHArchive() instance to run action on
            *args, **kwargs
                Arguments passed on to the action
        Returns: 
            Return value of this action
        """
        raise NotImplementedError
    
    def _join(self, results):
        """
        Protected function used to join the results of a list of run_singles. 
        By default simply returns the list. 
        
        Arguments:
            results
                A list of results to join
        Returns:
            An object representing the join of the results. 
        """
        return results
    
    def run_all(self, archives, *args, **kwargs):
        """
        Runs this action on a list of archives. By default forwards to self.run_single()
        . Needs to be implemented by subclass. 
        
        Arguments:
            archives
                List of LMHArchive() instances to run over
            *args, **kwargs
                Arguments passed on to the action
        Returns: 
            A single return value
        """
        
        return self._join([
            self.run_single(ra, *args, **kwargs)
            for ra in archives
        ])

class LocalArchiveAction(ArchiveBasedAction):
    """
    Represents an action that runs on individual local repositories. 
    """
    
    def run(self, archives, *args, **kwargs):
        """
        Runs this action on a list of local archives. Needs to be implemented
        by subclass. 
        
        Arguments:
            archives
                List of Strings, Pairs or LMHLocalArchive() instances to run over
            *args, **kwargs
                Arguments passed on to the action
        Returns: 
            Return value of this action
        """
        
        return self.run_all(self.manager.resolve_local_archives(*archives), *args, **kwargs)

class RemoteArchiveAction(ArchiveBasedAction):
    """
    Represents an action that runs on individual remote repositories. 
    """
    
    def run(self, archives, *args, **kwargs):
        """
        Runs this action on a single remote archive. Needs to be implemented
        by subclass. 
        
        Arguments:
            archives
                List of Strings, Pairs or LMHRemoteArchive() instances to run over
            *args, **kwargs
                Arguments passed on to the action
        Returns: 
            Return value of this action
        """
        
        return self.run_all(self.manager.resolve_remote_archives(*archives), *args, **kwargs)