class StandardActions(object):
    @staticmethod
    def register_to(manager):
        """
        Registers all standard actions to the given Manager() instance. 
        
        Arguments:
            manager
                Manager() to register all standard actions to
        """
        
        # External Program Actions
        from lmh.actions.program import git
        manager.add_action(git.GitAction())
        
        # Managment Actions
        from lmh.actions.management import listing
        manager.add_action(listing.LocalListAction())
        manager.add_action(listing.RemoteListAction())
        
        from lmh.actions.management import dtree
        manager.add_action(dtree.DependencyTreeAction())
        manager.add_action(dtree.DependencyTreePrintAction())