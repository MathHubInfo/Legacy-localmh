from lmh.actions import action
from lmh.utils import exceptions

class ArchiveBasedAction(action.Action):
    """
    Common Base Class for ArchiveBasedActions. 
    """
    def __init__(self, name, config, support_all = True):
        """
        Creates a new ArchiveBasedAction() instance. 
        
        Arguments: 
            name
                Name of this action
            config
                A list of LMHConfigSettingSpec() instances representing 
                configuration options needed by this action. 
            support_all
                Optional. Boolean indicating if the action is supported for all archives
                at once by giving an empty list of archives. Default to True. 
        """
        
        super(ArchiveBasedAction, self).__init__(name, config)        
        self.__support_all = support_all
        
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
    
    def _resolve(self, *archives):
        """
        Protected function used to resolve a list of archives. To be overidden
        by subclass. 
        
        Arguments:
            *archives
                A list of string, LMHArchive() or pairs to resolve
        Returns:
            A list of archives
        """
        raise NotImplementedError
    
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
        
        if len(archives) == 0 and not self.__support_all:
            raise AtLeastOneArchiveRequiredException
        
        return self.run_all(self._resolve(*archives), *args, **kwargs)

class LocalArchiveAction(ArchiveBasedAction):
    """
    Represents an action that runs on individual local archives. 
    """
    
    def _resolve(self, *archives):
        """
        Protected function used to resolve a list of archives. 
        
        Arguments:
            archives
                A list of string, LMHArchive() or pairs to resolve
        Returns:
            A list of archives
        """
        return self.manager.resolve_local_archives(*archives)

class RemoteArchiveAction(ArchiveBasedAction):
    """
    Represents an action that runs on individual remote archives. 
    """
    
    def _resolve(self, *archives):
        """
        Protected function used to resolve a list of archives. 
        
        Arguments:
            archives
                A list of string, LMHArchive() or pairs to resolve
        Returns:
            A list of archives
        """
        
        return self.manager.resolve_remote_archives(*archives)

class AtLeastOneArchiveRequiredException(exceptions.LMHException):
    """
    Exception thrown to indicate that at least one archive argument is required. 
    """
    
    def __init__(self):
        """
        Creates a new AtLeastOneArchiveRequiredException() instance
        """
        super(AtLeastOneArchiveRequiredException, self).__init__("at least one archive is required as argument. ")