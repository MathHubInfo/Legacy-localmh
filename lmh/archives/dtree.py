from lmh.utils.clsutils.caseclass import caseclass

from lmh.logger import escape
from lmh.archives import manifest

from collections import deque
from lmh.utils import tree

@caseclass
class DependencyNode(tree.TreeNode):
    """
    Represents a single node in the dependency tree. 
    """
    
    @staticmethod
    def build(archive, dependency_key = None, shallow = True, sort_nodes = True, summarize_unexpanded_nodes = True, summarize_circular_nodes = False):
        """
        Builds a dependency tree for local archives. 
        
        Arguments:
            archive
                LMHArchive() instance to build tree of
            dependency_key
                Optional. By default dependencies will be resolved by calling
                archive.dependencies. If you want to have custom dependency
                resolution, a function which takes an archive and returns a list
                of dependent archives can be given here. If the function should
                return None. 
            shallow
                Optional. By default it will keep the tree as shallow as 
                possible by doing a fringe first expansion. If this parameter is
                set to false a full expansion will performed in where only 
                CirucluarDependencies will be left non-expanded. 
            sort_nodes
                Optional. By default the children of each node will be sorted
                alphabetically and by type of node. If set to False nodes will 
                be returned in the original order. 
            summarize_unexpanded_nodes
                Optional. By default unexpanded nodes will be grouped together. 
                Set this parameter to False to supress this behaviour. 
            summarize_circular_nodes
                Optional. If set to true circular nodes will be grouped together
        Returns:
            A DependencyNode() object representing the shallow dependency tree. 
        """
        
        tree = DependencyNode.__build_shallow(archive, dependency_key=dependency_key) if shallow else DependencyNode.__build_deep(archive, dependency_key=dependency_key)
        
        # sort nodes if requested
        if sort_nodes:
            tree.sort_children()
        
        # summarize nodes if requested
        if summarize_unexpanded_nodes:
            tree.summarise_unexpanded_nodes()
        
        if summarize_circular_nodes:
            tree.summarise_circular_nodes()
        
        # return the tree
        return tree
    
    @staticmethod
    def __default_dependency_key(archive):
        """
        The default dependency_key function for __build_shallow() and __build_deep().
        
        Arguments:
            archive
                Archive to check dependencies from. 
        Returns:
            A list of dependent archives or None. 
        """
        
        if not archive.is_local():
            return None
        else:
            try:
                return archive.to_local_archive().dependencies
            except manifest.NoManifestFile:
                return []
        
    
    @staticmethod
    def __build_shallow(archive, dependency_key = None):
        """
        Itertively builds a shallow dependency tree for local archives with a 
        fringe-first expansion.
        
        Arguments:
            archive
                LMHArchive() instance to build tree of
            dependency_key
                Optional. By default dependencies will be resolved by calling
                archive.dependencies. If you want to have custom dependency
                resolution, a function which takes an archive and returns a list
                of dependent archives can be given here. If the function should
                return None. 
        Returns:
            A DependencyNode() object representing the shallow dependency tree. 
        """
        
        if dependency_key == None:
            dependency_key = DependencyNode.__default_dependency_key
        
        # get the initial dependencies
        inital_deps = dependency_key(archive)
        
        # if it is missing, we are done already
        if inital_deps == None:
            return DependencyNode(MissingDependency(archive))
        
        # the root node we will use
        root = DependencyNode(InstalledDependency(archive))
        
        # quqes for nodes and dependencies
        nodeq = deque([(root, [str(archive)], inital_deps)])
        
        # list of known archives
        known_archives = []
        
        while(len(nodeq) != 0):
            
            # take the current node and dependencies
            (node, circ, deps) = nodeq.popleft()
            
            # add the archive to the known archives
            known_archives.append(str(node.data.archive))
            
            # for each dependency
            for a in deps:
                
                # if we know the node already it will either not be expanded or
                # is circular
                if str(a) in known_archives:
                    if str(a) in circ:
                        here = DependencyNode(CircularDependency(a))
                    else:
                        here = DependencyNode(UnexpandedDependency(a))
                    node.children.append(here)
                    continue
                
                # else we need to get the dependencies
                a_deps = dependency_key(a)
                a_circ = circ + [str(a)]
                
                # if we have the dependencies we can append a new node
                if a_deps != None:
                    known_archives += [str(a)]
                    
                    a_node = DependencyNode(InstalledDependency(a))
                    node.children.append(a_node)
                    
                    nodeq.append((a_node, a_circ, a_deps))
                
                # else it is missing and we do not need to expand it further
                else: 
                    known_archives += [str(a)]
                    
                    a_node = DependencyNode(MissingDependency(a))
                    node.children.append(a_node)
        
        return root
    
    @staticmethod
    def __build_deep(archive, dependency_key = None, known = None):
        """
        Recursively builds a deep dependency tree for local archives with a 
        depth-first expansion. 
        
        Arguments:
            archive
                LMHArchive() instance to build tree of
            dependency_key
                Optional. By default dependencies will be resolved by calling
                archive.dependencies. If you want to have custom dependency
                resolution, a function which takes an archive and returns a list
                of dependent archives can be given here. If the function should
                return None. 
            known
                List of known archives that should not be expanded. 
        Returns:
            A DependencyNode() object representing the deep dependency tree. 
        """
        
        if known == None:
            known = []
        
        if dependency_key == None:
            dependency_key = DependencyNode.__default_dependency_key
        
        # if we know it we are done
        if str(archive) in known:
            return DependencyNode(CircularDependency(archive))
        
        # get dependencies
        dependencies = dependency_key(archive)
        
        # if we can not resolve them we can mark them as missing
        if dependencies == None:
            return DependencyNode(MissingDependency(archive))
        
        # else we are installed
        node = DependencyNode(InstalledDependency(archive))
        
        # we know this node now, no more need to expand it
        deep_known = known + [str(archive)]
        
        # add the children
        node.children = [
            DependencyNode.__build_deep(a, dependency_key = dependency_key, known = deep_known) for a in dependencies
        ]
        
        # and return the node
        return node
    
    def __init__(self, data):
        """
        Creates a new DependencyNode() instance. 
        
        Arguments:
            data
                DependencyData() contained in this DependencyNode()
        """
        self.data = data
        self.children = []
    
    def summarise_circular_nodes(self):
        """
        Summarises Circular Nodes in place
        
        Returns: 
            A new node object with the summarise circular nodes
        """
        
        return self.summarise_nodes(CircularDependency, MultipleCircularDependency)
    
    def summarise_unexpanded_nodes(self):
        """
        Summarises Unexpanded Nodes in place
        """
        
        return self.summarise_nodes(UnexpandedDependency, MultipleUnexpandedDependency)
    
    def summarise_nodes(self, haystack_class, replace_class):
        """
        Summarises children of a specific class and groups instances together
        in-place. 
        
        Arguments:
            haystack_class
                Class of objects to group together
            replace_class
                Class of objects that are grouped together
        """
        
        # set some flags
        is_tp = False
        
        # iterate through the children manually
        i = 0
        while i < len(self.children):
            
            # summarise nodes of the children first
            self.children[i].summarise_nodes(haystack_class, replace_class)
            
            if isinstance(self.children[i].data, haystack_class):
                if not is_tp:
                    # replace the child with a summarised node
                    child = self.children[i]
                    self.children[i] = DependencyNode(replace_class([child.data.archive]))
                    self.children[i].children = child.children
                    del child
                    
                    # set the flag and increate the counter
                    is_tp = True
                    i = i + 1
                else:
                    # pop the current element and add it to the previous one
                    child = self.children.pop(i)
                    self.children[i - 1].data.archives += [child.data.archive]
                    self.children[i - 1].children += child.children
                    del child
            else:
                # reset the flag and continue to the next iteration
                is_tp = False
                i = i + 1
    
    def sort_children(self):
        """
        Sorts the children of this node by type and then by name in-place
        """
        
        # sort the children alphabetically
        self.children.sort(key=lambda n:str(n.data))
        
        # initialise buckets for the children
        children_installed = []
        children_missing = []
        children_unexpanded = []
        children_circular = []
        
        # go over each of the child nodes
        for (i, c) in enumerate(self.children):
            
            # sort them
            c.sort_children()
            
            # and put their indexes into buckets
            if isinstance(c.data, InstalledDependency):
                children_installed.append(i)
            elif isinstance(c.data, MissingDependency):
                children_missing.append(i)
            elif isinstance(c.data, UnexpandedDependency) or isinstance(c.data, MultipleUnexpandedDependency):
                children_unexpanded.append(i)
            elif isinstance(c.data, CircularDependency) or isinstance(c.data, MultipleCircularDependency):
                children_circular.append(i)
        
        # reorder the children in place
        self._reorder_children(children_installed + children_missing + children_circular + children_unexpanded)
    
@caseclass
class DependencyData(object):
    """
    BaseClass for all items inside the dependency node
    """
    pass

@caseclass
class DependentArchive(DependencyData):
    """
    Base Class representing a single dependent archive. 
    """
    def __init__(self, archive):
        """
        Creates a new DependentArchive() instance.
        
        Arguments:
            archive
                LMHArchive() instance that is wrapped
        """
        self.archive = archive

@caseclass
class InstalledDependency(DependentArchive):
    """
    Represents an installed dependency
    """
    def __str__(self):
        """
        Turns this object into a string. 
        
        Returns:
            a string
        """
        return '[%s]' % (escape.Green(self.archive),)

@caseclass
class MissingDependency(DependentArchive):
    """
    Represents a missing dependency
    """
    def __str__(self):
        """
        Turns this object into a string. 
        
        Returns:
            a string
        """
        return '[%s] (missing)' % (escape.Red(self.archive),)

@caseclass
class CircularDependency(DependentArchive):
    """
    Represents a dependency that was skipped because it would be circular
    """
    def __str__(self):
        """
        Turns this object into a string. 
        
        Returns:
            a string
        """
        return '[%s] (circular)' % (escape.Yellow(self.archive),)

@caseclass
class UnexpandedDependency(DependentArchive):
    """
    Represents a dependency that was not expanded to keep the tree shallow. 
    """
    def __str__(self):
        """
        Turns this object into a string. 
        
        Returns:
            a string
        """
        return '[%s] (unexpanded)' % (escape.Blue(self.archive),)

@caseclass
class SummarizedDependency(DependencyData):
    """
    Base Class representing a multiple dependent archives that have been summarized
    """
    def __init__(self, archives):
        """
        Creates a new DependentArchive() instance.
        
        Arguments:
            archive
                LMHArchive() instance that is wrapped
        """
        self.archives = archives

class MultipleUnexpandedDependency(SummarizedDependency):
    """
    Represents multiple unexpanded dependencies
    """
    def __str__(self):
        """
        Turns this object into a string. 
        
        Returns:
            a string
        """
        
        if len(self.archives) >= 3:
            names = '%s ... %s' % (escape.Blue(self.archives[0]), escape.Blue(self.archives[-1]))
        else:
            names = ' '.join(list(map(escape.Blue, self.archives)))
        
        return '[%s] (%d unexpanded)' % (names,len(self.archives))

@caseclass
class MultipleCircularDependency(MultipleUnexpandedDependency):
    """
    Represents multiple circular dependencies
    """
    def __str__(self):
        """
        Turns this object into a string. 
        
        Returns:
            a string
        """
        
        if len(self.archives) >= 3:
            names = '%s ... %s' % (escape.Yellow(self.archives[0]), escape.Yellow(self.archives[-1]))
        else:
            names = ' '.join(list(map(escape.Yellow, self.archives)))
        
        return '[%s] (%d circular)' % (names, len(self.archives))