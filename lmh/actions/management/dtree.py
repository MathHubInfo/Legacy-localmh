from lmh.actions import archive
from lmh.actions.management import management
from lmh.logger import escape
from lmh.archives import manifest

from lmh.utils.clsutils.caseclass import caseclass

from collections import deque

class DependencyTreeAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that builds local dependency trees. 
    """
    
    def __init__(self):
        """
        Creates a new LocalListAction() instance. 
        """
        super(DependencyTreeAction, self).__init__('deps-tree', [])
    
    def run_single(self, archive, shallow = True):
        """
        Itertively builds a dependency tree for local archives. 
        
        Arguments:
            archive
                LMHArchive() instance to build tree of
            shallow
                Optional. By default it will keep the tree as shallow as 
                possible by doing a fringe first expansion. If this parameter is
                set to false a full expansion will performed in where only 
                CirucluarDependencies will be left non-expanded. 
        Returns:
            A DependencyNode() object representing the shallow dependency tree. 
        """
        
        return self.run_single_shallow(archive) if shallow else self.run_single_deep(archive)
    
    def run_single_shallow(self, archive, known = []):
        """
        Itertively builds a shallow dependency tree for local archives with a 
        fringe-first expansion.
        
        Arguments:
            archive
                LMHArchive() instance to build tree of
        Returns:
            A DependencyNode() object representing the shallow dependency tree. 
        """
        
        # the root node we will use
        root = DependencyNode(InstalledDependency(archive) if archive.is_local() else MissingDependency(archive) )
        
        # q of nodes we will use for expansion
        node_q = deque([root])
        
        # list of known archives
        known_archives = []
        
        while(len(node_q) != 0):
            
            # take the current node
            now = node_q.popleft()
            
            # add the archive to the known archives
            known_archives.append(str(now.data.archive))
            
            # for each dependency
            for a in now.data.archive.to_local_archive().get_dependencies():
                
                # if we know it already it is cirular
                if str(a) in known_archives:
                    here = DependencyNode(UnexpandedDependency(a))
                    now.children.append(here)
                
                # else if it is local, we can add it
                elif a.is_local():
                    known_archives += [str(a)]
                    
                    here = DependencyNode(InstalledDependency(a))
                    now.children.append(here)
                    node_q.append(here)
                
                # else it is missing and we cant do much
                else: 
                    known_archives += [str(a)]
                    
                    here = DependencyNode(MissingDependency(a))
                    now.children.append(here)
        
        return root
    
    def run_single_deep(self, archive, known = []):
        """
        Recursively builds a deep dependency tree for local archives with a 
        depth-first expansion. 
        
        Arguments:
            archive
                LMHArchive() instance to build tree of
            known
                List of known archives that should not be expanded. 
        Returns:
            A DependencyNode() object representing the deep dependency tree. 
        """
        
        # if the archive is not local we can miss it immediatly
        if not archive.is_local():
            return DependencyNode(MissingDependency(archive))
        
        # if we know it we are done
        if str(archive) in known:
            return DependencyNode(CircularDependency(archive))
        
        # else we are installed
        node = DependencyNode(InstalledDependency(archive))
        
        # we know this node now, no more need to expand it
        deep_known = known + [str(archive)]
        
        # add the children
        node.children = [
            self.run_single_deep(a, deep_known) for a in archive.to_local_archive().get_dependencies()
        ]
        
        # and return the node
        return node

class DependencyTreePrintAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that prints (local) dependency trees
    """
    
    def __init__(self):
        """
        Creates a new LocalListAction() instance. 
        """
        super(DependencyTreePrintAction, self).__init__('print-deps-tree', [])
    
    def run_single(self, archive, shallow = True):
        """
        Prints the dependency tree for local archives. 
        
        Arguments:
            archive
                LMHArchive() instance to build tree of
            shallow
                Optional. By default it will keep the tree as shallow as 
                possible by doing a fringe first expansion. If this parameter is
                set to False a full expansion will performed in where only 
                CirucluarDependencies will be left non-expanded. 
        """
        
        dtree = self.manager['deps-tree'].run_single(archive, shallow = shallow)
        
        self.manager.logger.log(self.print_tree_node(dtree))
        
        return None
        
    def print_tree_node(self, node, prefix = ''):
        """
        Returns the string representing a single tree node
        """
        
        CHAR_DEPS_MULTIPLE = '├'
        CHAR_DEPS_SINGLE   = '└'
        CHAR_DEPS_EXPAND   = '─'
        CHAR_DEPS_LINEAR   = '│'
        
        clean_prefix = prefix[:].replace(CHAR_DEPS_MULTIPLE, CHAR_DEPS_LINEAR).replace(CHAR_DEPS_EXPAND, ' ').replace(CHAR_DEPS_SINGLE, ' ')
        
        # name of the archive
        data = node.data
        name = str(data.archive)
        children = node.children
        
        if isinstance(data, MissingDependency):
            # [repo] missing
            return '%s[%s] missing' % (prefix, escape.Red(name))
        
        elif isinstance(data, UnexpandedDependency):
            # [repo] skipped
            return '%s[%s] unexpanded' % (prefix, escape.Blue(name))
        
        elif isinstance(data, CircularDependency):
            # [repo] circular
            return '%s[%s] circular' % (prefix, escape.Yellow(name))
            
        elif isinstance(data, InstalledDependency):
            # [repo]
            # +-- <repo2>
            # +-- ...
            # +-- <repoN>
            
            selfnode = '%s[%s]' % (prefix, escape.Green(name))
            
            if len(children) == 0:
                # <repo>
                return selfnode
            
            onenode = lambda n:self.print_tree_node(n, prefix = '%s%s%s%s' % (clean_prefix, CHAR_DEPS_MULTIPLE, CHAR_DEPS_EXPAND, CHAR_DEPS_EXPAND))
            nodes = list(map(onenode, children[:-1]))
            
            lastnode = self.print_tree_node(children[-1], prefix = '%s%s%s%s' % (clean_prefix, CHAR_DEPS_SINGLE, CHAR_DEPS_EXPAND, CHAR_DEPS_EXPAND))
            
            return '\n'.join([selfnode] + nodes + [lastnode])

@caseclass
class DependencyNode(object):
    """
    Represents a node in the DependencyTree. 
    """
    def __init__(self, data):
        """
        Creates a new DependencyNode() instance. 
        
        Arguments:
            data
                DependencyData() contained in this DependencyNode()
        """
        self.data = data
        self.children = []
    
@caseclass
class DependencyData(object):
    """
    Base class for DependencyNode objects in the DependencyTree. 
    """
    def __init__(self, archive):
        """
        Creates a new DependencyData() object. 
        
        Arguments:
            archive
                LMHArchive() instance that is wrapped
        """
        self.archive = archive
    
    def __str__(self):
        """
        Turns this object into a string. 
        
        Returns:
            a string
        """
        return str(self.archive)

@caseclass
class InstalledDependency(DependencyData):
    """
    Represents an installed dependency
    """
    pass

@caseclass
class MissingDependency(DependencyData):
    """
    Represents a missing dependency
    """
    pass

@caseclass
class UnexpandedDependency(DependencyData):
    """
    Represents a dependency that was not expanded to keep the tree shallow. 
    """
    pass

@caseclass
class CircularDependency(DependencyData):
    """
    Represents a dependency that was skipped because it would be circular
    """
    pass