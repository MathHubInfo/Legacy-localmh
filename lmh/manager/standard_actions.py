class StandardActions(object):
    @staticmethod
    def register_to(manager):
        """
        Registers all standard actions to the given Manager() instance. 
        
        Arguments:
            manager
                Manager() to register all standard actions to
        """
        
        # Core actions
        from lmh.actions.core import info, config
        manager += info.InfoAction()
        
        manager += config.GetConfigInfoAction()
        manager += config.GetConfigAction()
        manager += config.SetConfigAction()
        manager += config.ResetConfigAction()
        
        # External Program Actions
        from lmh.actions.program import git
        manager += git.GitAction()
        
        # Managment Actions
        from lmh.actions.management import listing
        manager += listing.LocalListAction()
        manager += listing.RemoteListAction()
        
        from lmh.actions.management import dtree
        manager += dtree.DependencyTreeAction()
        manager += dtree.DependencyTreePrintAction()
        
        from lmh.actions.management import install
        manager += install.InstallAction()