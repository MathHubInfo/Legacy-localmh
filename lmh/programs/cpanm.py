from lmh.programs import program

import sys
import os, os.path
import subprocess

from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class CPANM(program.Program):
    """
    Represents an interface to cpanm.
    """
    def __init__(self, cpanm_executable = "cpanm"):
        """
        Creates a new CPANM() instance.

        Arguments:
            cpanm_executable
                Optional. Name of the git executable. Defaults to "cpanm".
        """

        self.__executable = program.Program.which(cpanm_executable)
        self.__encoding = "utf-8" # TODO: We might not want to hardcode

        if self.__executable == None:
            raise CPANMNotFound()
        
class CPANMNotFound(Exception):
    """
    Exception that is thrown when cpanm is not found
    """
    
    def __init__(self):
        super(CPANMNotFound, self).__init__("Can not find cpanm")
