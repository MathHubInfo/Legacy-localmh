from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class TreeNode(object):
    def __init__(self, data = '╿', children = None):
        """
        Creates a new TreeNode. 
        
        Arguments:
            data
                Data Node for this TreeNode
            children
                List of children of this TreeNode. Optional, defaults to the empty
                list. 
        """
        
        self.data = data
        self.children = children if children != None else []
    def __str__(self):
        """
        Same as self.treestr()
        """
        return self.treestr()
        
    def treestr(self, prefix = '', other_prefix = ''):
        """
        Returns a nicely-formatted string representing this DependencyTree. 
        
        Arguments:
            prefix, other_prefix
                FOR INTERNAL USE ONLY. Prefixes to prepend to all lines of the tree. 
        
        Returns:
            a string
        """
        
        # Visualise the node itself
        treestr = '%s%s' % (prefix, self.data)
        
        # if there are no children, we are done. 
        if len(self.children) == 0:
            return treestr
        
        # Prefixes for the not last lines
        nll_prefix  = '%s├──'% (other_prefix,)
        nll_oprefix = '%s│  ' % (other_prefix,)
        
        # now go through each of the children except the last one
        for c in self.children[:-1]:
            treestr += '\n' + c.treestr(prefix = nll_prefix, other_prefix = nll_oprefix)
        
        # Prefixes for the last line
        ll_prefix  = '%s└──' % (other_prefix, )
        ll_oprefix = '%s   ' % (other_prefix, )
        
        # Add the last line
        treestr += '\n' + self.children[-1].treestr(prefix = ll_prefix, other_prefix = ll_oprefix)
        
        # and return it
        return treestr
    def _reorder_children(self, order):
        """
        Changes the order of the children of this tree node in place. 
        
        Arguments:
            order
                List of index mappings for the new children
        """
        
        # adapted from http://stackoverflow.com/a/1683662
        done = [False for i in range(len(self.children))]
        
        for i in range(len(self.children)):
            if not done[i]:
                c = self.children[i]
                
                j = i
                while True:
                    done[j] = True
                    
                    if order[j] != i:
                        self.children[j] = self.children[order[j]]
                        j = order[j]
                    else:
                        self.children[j] = c
                        break
                
                del c

@caseclass
class PrintableTreeObject(object):
    """
    Represents an object in a tree that has
    a string representation and internal data. 
    """
    
    def __init__(self, data, s):
        """
        Creates a new PrintableTreeObject()
        
        Arguments:
            Data
                Data this node has
            s
                String representing this object
        """
        
        self.data = data
        self.s = s
    
    def __str__(self):
        """
        Turns this object into a string
        
        Returns:
            a string
        """
        return str(self.s)