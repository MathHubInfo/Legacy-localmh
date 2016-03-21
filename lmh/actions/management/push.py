from lmh.actions.management import management
from lmh.actions import archive
from lmh.archives import manifest, local, gbranch

from collections import deque

class PushAction(archive.LocalArchiveAction, management.ManagementAction):
    """
    An action that pushes one (or more) archives including their dependencies
    """
    
    def __init__(self):
        """
        Creates a new PushAction() instance. 
        """
        super(PushAction, self).__init__('push')
    
    def run_all(self, archives, generated_branches = True, dependencies = True, print_tree = True, confirm = True):
        """
        Pulls the given (local) archives including dependencies. 
        
        Arguments:
            archives
                List of LMHArchive() local instances to pull
            generated_branches
                Boolean indicating if generated content branches should be 
                pushed automatically. Defaults to False. 
            dependencies
                Boolean indicating if dependencies should be pushed as well. 
                Defaults to True
            print_tree
                Optional. Boolean indicating if a tree of installed
                archives should be printed after completion of pulling. 
                Defaults to True. 
            confirm
                Optional. If set to False will not prompt before pushing archives. 
        Returns:
            A list of archives that were checked during the process
        """
        
        # Archives in the quenue
        aq = deque(archives)
        
        # if there are no archives to pull, return
        if len(aq) == 0:
            self.manager.logger.log('There is nothing to do. Please check spelling of repository names. ')
            return None
        
        self.manager.logger.log('The following archives will be pushed: ')
        self.manager.logger.log(self.manager('ls-local', archives))
        
        if confirm:
            self.manager.logger.log('Do you want to continue? [y/N]', newline = False)
            c = input()
            
            if c.lower() != 'y':
                self.manager.logger.error('Operation aborted by user')
                return None
        
        # list of archives we pushed
        touched = []
        
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
                self.manager.logger.warn('Missing dependency found, can not push: %s' % (item), flush = True)
                
                continue
            
            # get the local archive
            la = item.to_local_archive()
            
            # do the actual pushing
            self.manager.logger.info('Pushing repository %s' % (item), flush = True)
            if not la.push(self.manager('git')):
                self.manager.logger.warn('Pushing failed for repository %s' % (item), flush = True)
            
            # handle generated branches
            if generated_branches:
                # TODO: Push all installed generated branches
                self.manager.logger.warn('Pushing generated branches %s: Unimplemented, skipping' % item, flush = True)
                
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
        
        # print a list of trees if requested
        if print_tree:
            tree = self.manager('highlight-archive-tree', touched, 'Archives that have been pushed to the remote', archives)
            self.manager.logger.log(tree)
        
        return touched
        