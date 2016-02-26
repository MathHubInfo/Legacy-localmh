from lmh.actions import archive
from lmh.actions.management import management
from lmh.archives import dtree
from lmh.utils import tree

class DependencyTreeAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that builds local dependency trees. 
    """
    
    def __init__(self):
        """
        Creates a new LocalListAction() instance. 
        """
        super(DependencyTreeAction, self).__init__('deps-tree', [])
    
    def run_single(self, archive, **kwargs):
        """
        Itertively builds a dependency tree for local archives. 
        
        Arguments:
            archive
                LMHArchive() instance to build tree of
            **kwargs
                Optional arguments to pass to DependencyNode.build()
        Returns:
            A DependencyNode() object representing the shallow dependency tree. 
        """
        
        return dtree.DependencyNode.build(archive, **kwargs)
    
    def _join(self, results):
        """
        Protected function used to join the results. 
        
        Arguments:
            results
                A list of dependency trees for the requested archives
        Returns:
            a single tree representing all requested dependencies
        """
        return tree.TreeNode(children = results)

class DependencyTreePrintAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that prints (local) dependency trees
    """
    
    def __init__(self):
        """
        Creates a new LocalListAction() instance. 
        """
        super(DependencyTreePrintAction, self).__init__('print-deps-tree', [])
    
    def run_all(self, archives, **kwargs):
        """
        Prints the dependency tree for local archives. 
        
        Arguments:
            archives
                List of LMHArchive() instances to print tree of
            **kwargs
                Optional arguments to pass to DependencyNode.build()
        Returns:
            A boolean indicating success
        """
        
        
        tree = self.manager('deps-tree', archives, **kwargs)
        self.manager.logger.log(tree)