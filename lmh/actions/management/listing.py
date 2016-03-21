from lmh.actions import archive
from lmh.actions.management import management
from lmh.logger import escape
from lmh.utils import tree

class ListAction(management.ManagementAction):
    """
    Common Base class for LocalListAction and RemoteListAction
    """
    
    def build_archive_tree(self, archives):
        """
        Builds a tree.TreeNode() object containing a instance/group/name tree
        for archives. The third level of nodes consists of tree.PrintableTreeObject()
        instances containing the archive object and the matching string representation. 
        
        Arguments:
            archives
                A list of archives to build the tree of
          
        Returns: 
            tree.TreeNode() object
        """
        
        root = tree.TreeNode()
        
        for a in archives:
            # find the instance child
            ic = None
            for c in root.children:
                if c.data == a.instance.name:
                    ic = c
                    break
            else:
                ic = tree.TreeNode(data = a.instance.name)
                root.children.append(ic)
                root.children.sort(key=lambda n:n.data)
            
            # find the group child
            gc = None
            for c in ic.children:
                if c.data == a.group:
                    gc = c
                    break
            else:
                gc = tree.TreeNode(data = a.group)
                ic.children.append(gc)
                ic.children.sort(key=lambda n:n.data)
            
            # and finally append the new child for the repo
            cn = tree.TreeNode(data = tree.PrintableTreeObject(a, a.name))
            gc.children.append(cn)
            gc.children.sort(key=lambda n:str(n.data))
        
        return root

class LocalListAction(archive.LocalArchiveAction, ListAction):
    """
    An action that returns a instance/group/name tree for local archives
    """
    
    def __init__(self):
        """
        Creates a new LocalListAction() instance. 
        """
        super(LocalListAction, self).__init__('ls-local')
    
    def run_all(self, archives):
        """
        Runs this action on all archives
        
        Arguments:
            archives
                LMHArchive() instances to run action on
        """
        
        return self.build_archive_tree(archives)
        
class RemoteListAction(archive.RemoteArchiveAction, ListAction):
    """
    An action that prints out all (matching) remote archives into the log. 
    """
    
    def __init__(self):
        """
        Creates a new RemoteListAction() instance. 
        """
        super(RemoteListAction, self).__init__('ls-remote')
        
    def run_all(self, archives):
        """
        Runs this action on all archives
        
        Arguments:
            archives
                LMHArchive() instances to run action on
        """
        
        return self.build_archive_tree(archives)

class HighlightedArchiveTreeAction(ListAction):
    """
    Archive used to create a highlighted archive tree
    """
    def __init__(self):
        """
        Creates a new HighlightedArchiveTreeAction() instance. 
        """
        super(HighlightedArchiveTreeAction, self).__init__('highlight-archive-tree')
    
    def run(self, archives, title, highlights, highlighter = None):
        """
        Creates a new highlighted archive tree
        
        Arguments:
            archives
                List of all archives and their dependencies to show in the 
                archive tree. Uses ls-local to find all matching repositories. 
            title
                Title for the root node of the tree
            highlights
                List of archives that should be highlighted in the tree
            highlighter
                Optional. Function to use to highlight archive names. Defaults to
                coloring the string green
        Returns:
            a TreeNode() object representing the given tree
        """
        
        # get the highlighter
        if highlighter == None:
            highlighter = escape.Green
        
        # build a tree of repositories
        root = self.manager('ls-local', archives)
        root.data += ' '+title
        
        # Turn it into a list of highlights
        highlight_names = list(map(str, highlights))
        
        # Iterate through the tree
        for ic in root.children:
            for gc in ic.children:
                gc.data = tree.PrintableTreeObject(0, gc.data)
                for (i, ac) in enumerate(gc.children):
                    archive = ac.data.data
                    if str(archive) in highlight_names:
                        ac.data.s = highlighter(archive.name)
                        ac.data.data = -1
                        gc.data.data += 1
                    else:
                        ac.data.data = 1
                gc.children.sort(key = lambda n:n.data.data)
            ic.children.sort(key = lambda n:n.data.data)
        return root