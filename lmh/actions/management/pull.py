from lmh.actions.management import management
from lmh.actions import archive
from lmh.logger import escape
from lmh.archives import manifest, local, gbranch
from lmh.utils import tree

from collections import deque

class PullAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that pulls one (or more) archives including their dependencies
    """
    
    def __init__(self):
        """
        Creates a new PullAction() instance. 
        """
        super(PullAction, self).__init__('pull')
    
    def run_all(self, archives, generated_branches = True, dependencies = True, install_missing = True, print_tree = True, confirm = True, rescan = True):
        """
        Pulls the given (local) archives including dependencies. 
        
        Arguments:
            archives
                List of LMHArchive() local instances to pull
            generated_branches
                Boolean indicating if generated content branches should be 
                updated / installed automatically. Defaults to True. 
            dependencies
                Boolean indicating if dependencies should be updated as well. 
                Defaults to True
            install_missing
                Boolean indicating it missing reposiories should be installed
                automatically. Defaults to True. 
            print_tree
                Optional. Boolean indicating if a tree of installed
                archives should be printed after completion of installation. 
                Defaults to True. 
            confirm
                Optional. If set to False will not prompt before updating archives. 
            generated_branches, dependencies, rescan
                Arguments to pass on to InstallAction() if needed
        Returns:
            A list of archives that were checked during the process
        """
        
        # Archives in the quenue
        aq = deque(archives)
        
        # if there are no archives to pull, return
        if len(aq) == 0:
            self.manager.logger.log('There is nothing to do. Please check spelling of repository names. ')
            return None
        
        self.manager.logger.log('The following archives will be updated: ')
        self.manager.logger.log(self.manager('ls-local', archives))
        
        if confirm:
            self.manager.logger.log('Do you want to continue? [y/N]', newline = False)
            c = input()
            
            if c.lower() != 'y':
                self.manager.logger.error('Operation aborted by user')
                return None
        
        # list of archives we installed
        touched = []
        
        # List of missing archives
        missing = []
        
        while len(aq) != 0:
            # get the next item
            item = aq.popleft()
            
            # if we already know the archive, keep going
            try:
                if item.to_local_archive() in touched:
                    continue
            except local.NoLocalArchive:
                pass
            
            # if the archive is not installed
            # we need to check if we can install it
            if not item.is_local():
                ra = item.to_remote_archive()
                
                if not ra in missing:
                    missing.append(ra)
                    
                    if install_missing:
                        self.manager.logger.info('Missing dependency found, queuing for installation: %s' % (item), flush = True)
                    else:
                        self.manager.logger.warn('Missing dependency found: %s' % (item), flush = True)
                
                continue
            
            # get the local archive
            la = item.to_local_archive()
            
            # do the actual pulling
            
            self.manager.logger.info('Pulling repository %s' % (item), flush = True)
            if not la.pull(self.manager('git')):
                self.manager.logger.warn('Pulling failed for repository %s' % (item), flush = True)
            
            # if requested, pull ü 
            if generated_branches:
                
                self.manager.logger.info('Updating generated branches for %s' % item, flush = True)
                
                # get the generated branch manager
                status = self.manager['gbranch-manager'].run_single(la).install_all(pull = True)
                
                # for each of them print some info
                for (k, s) in status:
                    if not s:
                        self.manager.logger.warn('Failed to update generated branch %s of %s' % (k, item), flush = True)
                    else:
                        self.manager.logger.info('Installed generated content branch %s of %s' % (k, item), flush = True)
                
            # add it to the touched repositories
            touched.append(la)
            
            # if requested, check for dependencies
            if dependencies:
                try:
                    deps = la.dependencies
                    for d in deps:
                        aq.append(d)
                    
                    if len(deps) == 1:
                        self.manager.logger.info('Found %2d %s of %s' % (len(deps), 'dependency' if len(deps) == 1 else 'dependencies', item))
                except manifest.NoManifestFile:
                    self.manager.logger.info('Archive %s has no MANIFEST.MF, skipping dependency scanning. ' % (item,), flush = True)
        
        # install the missing archives
        if install_missing and len(missing) > 0:
            self.manager.logger.info('Installing %s missing dependencies' % len(missing))
            
            install_touched = self.manager('install', missing, generated_branches = generated_branches, dependencies = dependencies, rescan = rescan, confirm = confirm, print_tree = False)
        else:
            install_touched = []
        
        # print a list of trees if requested
        if print_tree:
            tree = self.manager('highlight-archive-tree', touched + install_touched, 'Archives that are now up-to-date locally', archives)
            self.manager.logger.log(tree)
        
        return touched
        