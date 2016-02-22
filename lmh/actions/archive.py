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

class LocalArchiveAction(ArchiveBasedAction):
    """
    Represents an action that runs on individual local repositories. 
    """
    
    def run(self, archives, *args, **kwargs):
        """
        Runs this action on a single local archive. Needs to be implemented
        by subclass. 
        
        Arguments:
            archives
                List of Strings, Pairs or LMHLocalArchive() instances to run over
            *args, **kwargs
                Arguments passed on to the action
        Returns: 
            Return value of this action
        """
        
        return [
            self.run_single(ra, *args, **kwargs)
            for ra in self.manager.resolve_local_archives(*archives)
        ]

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
        
        return [
            self.run_single(ra, *args, **kwargs)
            for ra in self.manager.resolve_remote_archives(*archives)
        ]