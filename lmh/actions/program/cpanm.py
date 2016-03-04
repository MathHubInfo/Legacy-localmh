from lmh.actions.program import program
from lmh.programs import cpanm
from lmh.config import spec

class CPANMAction(program.ProgrammableAction):
    """
    An Action that wraps CPANM()
    """
    
    def __init__(self):
        """
        Creates a new CPANMAction()
        """
        super(CPANMAction, self).__init__('cpanm', spec.LMHConfigSettingSpec(
            'env::cpanm', 
            'string', 
            'cpanm', 
            'Path to the cpanm executable'
        ))
    
    def _register(self):
        """
        Protected Function that is called when this action is registered. 
        """
        try:
            self._program = cpanm.CPANM()
        except cpanm.CPANMNotFound:
            self._program = None
            self.manager.logger.warn('CPANM Executable not found. Please ensure that the %r setting is correct. ' % 'self.cpanm')