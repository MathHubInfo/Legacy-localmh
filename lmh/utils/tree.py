from typing import Optional, List, Any

from lmh.utils.clsutils.caseclass import caseclass


@caseclass
class TreeNode(object):
    """ Represents a printable tree node. """
    def __init__(self, data : Any = '╿', children : Optional[List] = None):
        """
        Creates a new tree node.

        :param data: Data associated to this TreeNode.
        :param children: List of children of this treeNode or none.
        """

        self.data = data
        self.children = children if children != None else []

    def __str__(self) -> str:
        """
        Turns this TreeNode into a nicely formatted string.
        """
        return self.__treestring()
        
    def __treestring(self, prefix : str ='', other_prefix : str ='') -> str:
        """
        Returns a nicely-formatted string representing this TreeNode.

        :param prefix: Prefix to preprend to the first line of the output.
        :param other_prefix: Prefix to prepend to other lines of the output.
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
            treestr += '\n' + c.__treestring(prefix = nll_prefix, other_prefix = nll_oprefix)
        
        # Prefixes for the last line
        ll_prefix  = '%s└──' % (other_prefix, )
        ll_oprefix = '%s   ' % (other_prefix, )
        
        # Add the last line
        treestr += '\n' + self.children[-1].__treestring(prefix = ll_prefix, other_prefix = ll_oprefix)
        
        # and return it
        return treestr

    def reorder_children(self, order : List[int]) -> None:
        """
        Changes the order of the children of this TreeNode in place.

        :param order: List of indexes to use for new order.
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
    """ Represents an object in a tree that has a string representation and internal data. """
    
    def __init__(self, data : Any, s : str):
        """
        Creates a new PrintableTreeObject().

        :param data: Data associated to this PrintableTreeObject.
        :param s: String representing this object.
        """
        
        self.data = data
        self.s = s
    
    def __str__(self):
        """ Turns this PrintableTreeObject into a string. """

        return str(self.s)