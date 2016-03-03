from lmh.actions.program import program
from lmh.external.programs import git
from lmh.config import spec

class GitAction(program.ProgrammableAction):
    """
    An Action that wraps Git()
    """
    
    def __init__(self):
        """
        Creates a new Git() action
        """
        super(GitAction, self).__init__('git', [
            spec.LMHConfigSettingSpec(
                'env::git', 
                'string', 
                'git', 
                'Path to the git executable'
            )
        ])
    
    def _register(self):
        """
        Protected Function that is called when this action is registered. 
        """
        try:
            self._program = git.Git(self.manager('get-config', 'env::git'))
        except:
            self._program = None
            self.manager.logger.warn('Git Executable not found. Please ensure that the %r setting is correct. ' % 'env::git')