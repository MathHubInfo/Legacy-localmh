import os.path
import subprocess

from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class Program(object):
    """
    BaseClass for interfaces to external programs used by lmh.
    """
    
    def __init__(self, systems_dir, sty_dir):
        """
        Creates a new Environment. 
        
        Arguments:
            systems_dir
                Directory to find systems in
            sty_dir
                Directory to find sty files in
        """
        
        self._systems = systems_dir
        self._sty = sty_dir
        self.__perl5env = None

    @staticmethod
    def which(program):
        """
        Returns the full path to a program that can be found in the users $PATH
        variable. Similar to the *nix command which (or the windows command where).
        Throws ExecutableNotFound if the executable can not be found
        
        Arguments:
            program
                A string containing the name of a program. May or may not be a
                full path.
        Returns:
            A string representing the full path to the given program or None.
        """

        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)

        if fpath and is_exe(program):
            return program

        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        # #Windows support: It might be an exe
        # if os.name == "nt" and not program.endswith(".exe"):
        #     return Program.which(program+".exe")
        
        raise ExecutableNotFound()
    
    def __perl5env__(self):
        """
        Returns a cached version of the perl5 environment variables
        
        Returns:
            a dict containing variables required for perl5 to run properly
        """
        # if we have the cache, return
        if self.__perl5env != None:
            return self.__perl5env
        
        # else create it
        self.__perl5env = {}
        
        # perl5root
        p5root = [os.path.join(self._systems, 'perl5lib')]
        
        # perl5bin
        p5bin = [
            os.path.join(self._systems, 'LaTeXML', 'bin'),
            os.path.join(self._systems, 'LaTeXMLs', 'bin')
        ] + [os.path.join(rd, 'bin') for rd in p5root]
        
        self.__perl5env['PATH'] = os.pathsep.join(p5bin)
        
        # perl5lib
        p5lib = [
            os.path.join(self._systems, 'LaTeXML', 'blib', 'lib'),
            os.path.join(self._systems, 'LaTeXMLs', 'blib', 'bin')
        ] + [os.path.join(rd, 'lib', 'perl5') for rd in p5root]
        
        self.__perl5env['PERL5LIB'] = os.pathsep.join(p5bin)
        
        # Set the sTeX sty dir
        stexstydir = os.path.join(self._systems, 'sTeX', 'sty')
        self.__perl5env['STEXSTYDIR'] = stexstydir
        
        # Set up the latexmlstydir
        latexmlstydir = os.path.join(self._systems, 'LaTeXML', 'lib', 'LaTeXML', 'texmf')
        
        # inuts for tex
        texinputs = ['.', self._sty]
        
        texinputs += [r for (r, f, d) in os.walk(stexstydir)]
        texinputs += [r for (r, f, d) in os.walk(latexmlstydir)]
        
        texinputs += [latexmlstydir, stexstydir]
        
        self.__perl5env['TEXINPUTS'] = os.pathsep.join(texinputs)
        
        # and return it
        return self.__perl5env
    
    def _env(self, env = None):
        """
        Sets up a proper environment for all build processes to run. 
        
        Arguments:
            env
                Base environment to start with. Defaults to os.environ.copy()
        returns:
            a dictionary containing the new environment
        """
        
        # set the default
        if env == None:
            env = os.environ.copy()
        
        # mixin the new values
        for (k, v) in self.__perl5env__().items():
            if k in env.keys():
                env[k] = '%s%s%s' % (v, os.pathsep, env[k])
            else:
                env[k] = v
        
        # and return
        return env
    
    def _popen(self, exc, *args, **kwargs):
        """
        Creates a subprocess.Popen handle with proper configuration for the 
        environment or throws ExecutableNotFound
        
        Arguments:
            exc
                Executable to run. Will be searched for in $PATH. 
            *args
                Arguments to pass to the executable
            **kwargs
                Arguments to pass to the Popen() call
        Returns:
            A subprocess.Popen handle
        """
        
        # find the executable
        exe = Program.which(exc)
        
        # if we can not find the executable, throw an error
        if exe == None:
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
    """
    Exception that is thrown when an Executable is not found
    """
    
    def __init__(self):
        super(ExecutableNotFound, self).__init__("Could not find the specefied executable")