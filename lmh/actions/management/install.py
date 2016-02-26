from lmh.actions.management import management
from lmh.actions import archive

class InstallAction(archive.RemoteArchiveAction, management.ManagementAction):
    """
    An action that installs one (or more) archives including their dependencies
    """
    
    def __init__(self):
        """
        Creates a new InstallAction() instance. 
        """
        super(InstallAction, self).__init__('install', [], support_all = False)
    
    def run_all(self, archives, dependencies = True, rescan = True, confirm = True):
        """
        Installs the given (remote) archives including dependencies. 
        
        Arguments:
            archives
                List of LMHArchive() remote instances to print tree of
            dependencies
                Optional. If set to False will not scan for dependencies. 
            rescan
                Optional. If set to True will scan already installed
                repositories for dependencies. 
            confirm
                Optional. If set to False will not prompt before installing archives. 
        Returns:
            An integer representing the number of new archives that has been installed
        """
        
        count = 0
        
        # Sort archives in local and remote
        local_archives = []
        remote_archives = []
        
        for a in archives:
            if a.is_local():
                local_archives.append(a)
            else:
                remote_archives.append(a)
        
        # print a log message of what we will do
        if len(remote_archives) > 0:
            self.manager.logger.log('The following archives will be installed: ')
            self.manager.logger.log('    %s' % ' '.join(list(map(str, remote_archives))))
        if rescan and len(local_archives) > 0:
            self.manager.logger.log('The following archives will be checked for missing dependencies: ')
            self.manager.logger.log('    %s' % ' '.join(list(map(str, local_archives))))
        
        
        # make a nice tree of installed repositories
        tree = self.manager('deps-tree', archives)
        tree.data += ' The following dependency tree was used'
        
        # and print it
        self.manager.logger.log(tree)
        self.manager.logger.log('Installed %d repositories' % count)
        
        return count
        
        