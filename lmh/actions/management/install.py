from lmh.actions.management import management
from lmh.actions import archive
from lmh.logger import escape
from lmh.archives import manifest, local, gbranch
from lmh.utils import tree

from collections import deque

class InstallAction(archive.RemoteArchiveAction, management.ManagementAction):
    """
    An action that installs one (or more) archives including their dependencies
    """
    
    def __init__(self):
        """
        Creates a new InstallAction() instance. 
        """
        super(InstallAction, self).__init__('install')
    
    def run_all(self, archives, generated_branches = True, dependencies = True, rescan = True, confirm = True):
        """
        Installs the given (remote) archives including dependencies. 
        
        Arguments:
            archives
                List of LMHArchive() remote instances to install
            generated_branches
                Boolean indicating if generated content branches should be 
                installed automatically. If set to False, they can be manually
                installed using the appropriate actions. 
            dependencies
                Optional. If set to False will not scan for dependencies. 
            rescan
                Optional. If set to False will only install missing repositories
                and not try to re-scan existing ones. This argument only applies
                to archives given to the function directly. 
            confirm
                Optional. If set to False will not prompt before installing archives. 
        Returns:
            A list of archives that were checked during the process
        """
        
        # Sort archives in local and remote
        local_archives = []
        remote_archives = []
        
        for a in archives:
            if a.is_local():
                local_archives.append(a)
            else:
                remote_archives.append(a)
        
        # Archives in the quenue
        aq = deque([])
        
        # print a log message of what we will do
        if len(remote_archives) > 0:
            self.manager.logger.log('The following archives will be installed: ')
            self.manager.logger.log(self.manager('ls-remote', remote_archives))
            for a in remote_archives:
                aq.append(a)
        if rescan and len(local_archives) > 0:
            self.manager.logger.log('The following archives will be checked for missing dependencies: ')
            self.manager.logger.log(self.manager('ls-local', local_archives))
            for a in local_archives:
                aq.append(a)
        
        # if we have nothing to do, return
        if len(aq) == 0:
            self.manager.logger.log('There is nothing to do. Please check spelling of repository names. ')
            return None
        
        # We might need to confirm with the user first
        if confirm:
            self.manager.logger.log('Do you want to continue? [y/N]', newline = False)
            c = input()
            
            if c.lower() != 'y':
                self.manager.logger.error('Operation aborted by user')
                return None
        
        # list of archives we installed
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
            
            # if the item is not local, install it first
            if not item.is_local():
                self.manager.logger.info('Installing %s from %s' % (item, item.resolve_remote()), flush = True)
                item.to_remote_archive().install(self.manager('git'))
            
            # get the local archive
            la = item.to_local_archive()
            
            # Install all generated branches if requested
            if generated_branches:
                
                self.manager.logger.info('Installing generated branches for %s' % item, flush = True)
                
                # get the generated branch manager
                status = self.manager['gbranch-manager'].run_single(la).install_all()
                
                # for each of them print some info
                for (k, s) in status:
                    if not s:
                        self.manager.logger.warn('Failed to install generated branch %s of %s: Already installed' % (k, item))
                    else:
                        self.manager.logger.info('Installed generated content branch %s of %s' % (k, item))
                
            # add it to the touched repositories
            touched.append(la)
            
            # check for dependencies
            if dependencies:
                try:
                    deps = la.dependencies
                    for d in deps:
                        aq.append(d)
                    
                    if len(deps) == 1:
                        self.manager.logger.info('Found %2d %s of %s' % (len(deps), 'dependency' if len(deps) == 1 else 'dependencies', item))
                except manifest.NoManifestFile:
                    self.manager.logger.info('Archive %s has no MANIFEST.MF, skipping dependency scanning. ' % (item,), flush = True)
        
        
        # make a nice tree of installed repositories
        root = self.manager('ls-local', touched)
        root.data += ' Archives that are now installed locally'
        
        # get a list of originally requested archives
        requested_archive_names = list(map(str, archives))
        
        # Mark the requested archives green and put them on top of the tree
        for ic in root.children:
            for gc in ic.children:
                gc.data = tree.PrintableTreeObject(0, gc.data)
                for (i, ac) in enumerate(gc.children):
                    archive = ac.data.data
                    if str(archive) in requested_archive_names:
                        ac.data.s = escape.Green(archive.name)
                        ac.data.data = -1
                        gc.data.data += 1
                    else:
                        ac.data.data = 1
                gc.children.sort(key = lambda n:n.data.data)
            ic.children.sort(key = lambda n:n.data.data)
        
        # and print it
        self.manager.logger.log(root)
        
        return touched
        