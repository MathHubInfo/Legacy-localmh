import os.path

class Program(object):
    """
    BaseClass for  interfaces to external programs used by lmh.
    """

    @staticmethod
    def which(program):
        """
        Returns the full path to a program that can be found in the users $PATH
        variable. Similar to the *nix command which (or the windows command where).

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

        return None
