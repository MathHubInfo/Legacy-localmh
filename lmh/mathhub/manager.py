from lmh.utils import exceptions

class MathHubManager(object):
    """
    Represents a Manager that can contain multiple MathHub Instances. 
    """
    
    def __init__(self, config):
        """
        Initalises a new MathHubManager() instance. 
        
        Arguments:
            config
                lmh.config.Config() instance that holds all the settings for this
                lmh instance
        """
        self.config = config
        
        self.__mathhubs = {}
    
    def addMathHubInstance(self, mh_instance):
        """
        Adds a new MathHubInstance() to this MathHubManager(). 
        
        Arguments:
            mh_instance
                MathHubInstance() to add to this controller. 
        """
        
        from lmh.mathhub import instance
        
        if not isinstance(mh_instance, instance.MathHubInstance):
            raise TypeError("mh_instance must be a MathHubInstance()")
        
        if mh_instance.name in self.__mathhubs.keys():
            raise InstanceAlreadyRegistered()
        
        self.__mathhubs[mh_instance.name] = mh_instance
    
    def getMathHubInstance(self, name):
        """
        Returns a MathHubInstance() that can resolve queries for the given
        name or throws InstanceNotFound(). 
        
        Arguments:
            name
                Name the instance should be able to answer queries for
        Returns:
            A MathHubInstance()
        """
        
        for (n, instance) in self.__mathhubs.items():
            if instance.can_answer_for(name):
                return instance
        
        raise InstanceNotFound()
    
    def resolve_local(self, *spec, base_group = None, instance = None):
        """
        Resolves the specification to a local repository within one or all 
        MathHubInstances() available in this MathHubManager() and returns triples of
        (instance, group, name) strings. 
        
        Arguments:
            *spec
                A list of strings or patterns contains *s that will be matched
                against the full names of repositories of the form 'group/name'.
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
            A list of triples of strings (instance, group, name) representing 
            repositories. 
        """
        
        if instance != None:
            return [
                (instance, g, n) for (g, n) in self.getMathHubInstance(instance).resolve_local(*spec, base_group = base_group)
            ]
        
        repos = set()
        
        for instance in self.__mathhubs.keys():
            repos.update(self.resolve_local(*spec, base_group = base_group, instance = instance))
        
        return list(sorted(repos))
    
    def get_local_path(self, instance, group, name):
        """
        Gets the (full) path to a local repository given by a triple. May throw
        InstanceNotFound or RepositoryNotFound. 
        
        Arguments:
            instance
                Name of instance to get full path to. 
            group
                Name of group to get full path to. 
            name
                Name of repository to find
        Returns:
            A string representing the full path to the given repository. 
        """
        
        return self.getMathHubInstance(instance).get_repo_path(group, name)
    
        
    def resolve_remote(self, *spec, base_group = None, instance = None):
        """
        Resolves the specification to a remote repository within one or all 
        MathHubInstances() available in this MathHubManager() and returns triples of
        (instance, group, name) strings. 
        
        Arguments:
            *spec
                A list of strings or patterns contains *s that will be matched
                against the full names of repositories of the form 'group/name'.
                If empty and base_group is None, the full list of repositories 
                will be returned. If empty and base_group has some value only
                repositories from that group will be returned. 
            base_group
                Optional. If given, before trying to match repositories globally
                will try to match 'name' inside the group base_group.
            intance
                Optional. If set returns only repositories from the 
                instance matching the given name. 
        Returns:
            A list of triples of strings (instance, group, name) representing 
            repositories. 
        """
        
        if instance != None:
            return [
                (instance, g, n) for (g, n) in self.getMathHubInstance(instance).resolve_remote(*spec, base_group = base_group)
            ]
        
        repos = set()
        
        for instance in self.__mathhubs.keys():
            repos.update(self.resolve_remote(*spec, base_group = base_group, instance = instance))
        
        return list(sorted(repos))
    
    def get_remote_path(self, instance, group, name):
        """
        Gets the (full) path to a remote repository given by a triple. May throw
        InstanceNotFound or RepositoryNotFound. 
        
        Arguments:
            instance
                Name of instance to get full path to. 
            group
                Name of group to get full path to. 
            name
                Name of repository to find
        Returns:
            A string representing the full path to the given repository. 
        """
        
        return self.getMathHubInstance(instance).get_repo_path(group, name)
        
class InstanceAlreadyRegistered(exceptions.MathHubException):
    """
    Exception that is thrown when a given instance is already registered in this
    MathHubManager().
    """
    def __init__(self):
        super(InstanceAlreadyRegistered, self).__init__('Instance already exists in this MathHubManager() instance. ')

class InstanceNotFound(exceptions.MathHubException):
    """
    Exception that is thrown when the given instance does not exist in this 
    MathHubManager(). 
    """
    def __init__(self):
        super(InstanceNotFound, self).__init__('Instance not found on this MathHubManager() instance. ')