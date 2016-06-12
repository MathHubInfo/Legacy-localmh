from typing import Dict, Optional, List, Any

import os.path
import subprocess

from lmh.utils.caseclass import caseclass


@caseclass
class Program(object):
    """ BaseClass for interfaces to external programs used by lmh. """

    @staticmethod
    def which(program: str) -> str:
        """ Returns the full path to a program that can be found in the users $PATH variable. Similar to the *nix
        command which (or the windows command where). Throws ExecutableNotFound if the executable can not be found.

        :param program: A string containing the name of a program. May or may not be a full path.
        """

        def is_exe(pth: str) -> bool:
            """ Checks if a file is executable. """
            return os.path.isfile(pth) and os.access(pth, os.X_OK)

        f_path, f_name = os.path.split(program)

        if f_path and is_exe(program):
            return program

        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        raise ExecutableNotFound()

    def __init__(self, systems_dir: str, sty_dir: str):
        """ Creates a new Program() instance.

        :param systems_dir: Directory to find systems in.
        :param sty_dir: Directory to find sty files in.
        """
        
        self._systems = systems_dir  # type: str
        self._sty = sty_dir # type: str
        self.__p5env = None  # type: Optional[Dict[str]]

    @property
    def perl5env(self) -> Dict[str, str]:

        # if we have it cached, return it
        if self.__p5env is not None:
            return self.__p5env

        self.__p5env = self.__perl5env()
        return self.__p5env
    
    def __perl5env(self) -> Dict[str, str]:
        """ Returns a dict containing variables required for perl5. """

        # Create a dict for the environment
        env = {}
        
        # perl5root
        p5root = [os.path.join(self._systems, 'perl5lib')]
        
        # perl5bin
        p5bin = [
            os.path.join(self._systems, 'LaTeXML', 'bin'),
            os.path.join(self._systems, 'LaTeXMLs', 'bin')
        ] + [os.path.join(rd, 'bin') for rd in p5root]

        env['PATH'] = os.pathsep.join(p5bin)
        
        # perl5lib
        p5lib = [
            os.path.join(self._systems, 'LaTeXML', 'blib', 'lib'),
            os.path.join(self._systems, 'LaTeXMLs', 'blib', 'bin')
        ] + [os.path.join(rd, 'lib', 'perl5') for rd in p5root]

        env['PERL5LIB'] = os.pathsep.join(p5bin)
        
        # Set the sTeX sty dir
        stexstydir = os.path.join(self._systems, 'sTeX', 'sty')
        env['STEXSTYDIR'] = stexstydir
        
        # Set up the latexmlstydir
        latexmlstydir = os.path.join(self._systems, 'LaTeXML', 'lib', 'LaTeXML', 'texmf')
        
        # inputs for tex
        texinputs = ['.', self._sty]
        
        texinputs += [r for (r, f, d) in os.walk(stexstydir)]
        texinputs += [r for (r, f, d) in os.walk(latexmlstydir)]
        
        texinputs += [latexmlstydir, stexstydir]

        env['TEXINPUTS'] = os.pathsep.join(texinputs)
        
        # and return it
        return env
    
    def _env(self, env: Optional[Dict[str, str]]=None) -> Dict[str, str]:
        """ Sets up a proper environment for all build processes to run.

        :param env: Optional. Base environment to start with. Defaults to os.environ.copy().
        """
        
        # set the default
        if env is None:
            env = os.environ.copy()
        
        # mixin the new values
        for (k, v) in self.perl5env.items():
            if k in env.keys():
                env[k] = '%s%s%s' % (v, os.pathsep, env[k])
            else:
                env[k] = v
        
        # and return
        return env
    
    def _popen(self, exc: str, *args: List[str], **kwargs: Dict[str, Any]) -> subprocess.Popen:
        """ Creates a subprocess.Popen handle with proper configuration for the environment or throws ExecutableNotFound.

        :param exc: Executable to run. Will be searched for in $PATH.
        :param args: Arguments to pass to the executable
        :param kwargs: Arguments to pass to the Popen() call
        """
        
        # find the executable
        exe = Program.which(exc)
        
        # if we can not find the executable, throw an error
        if exe is None:
            raise ExecutableNotFound()
        
        # popen arguments
        popen_args = [exe]+list(args)
        
        # Find the current base environment
        if 'env' in kwargs:
            base_env = kwargs.pop('env')
        else:
            base_env = os.environ.copy()
        
        # configure the environment properly
        kwargs['env'] = self._env(base_env)
        
        # make the popen call and return
        return subprocess.Popen(
            popen_args, **kwargs
        )


class ExecutableNotFound(Exception):
    """ Exception that is thrown when an Executable is not found. """
    
    def __init__(self):
        """ Creates a new ExecutableNotFound() instance. """
        super(ExecutableNotFound, self).__init__("Could not find the specefied executable")