from lmh.utils import fileio, exceptions

import os.path

from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class Manifest(object):
    """
    Represents the Manifest.MF file of an archive
    """
    
    def __init__(self, filename):
        """
        Creates a new Manifest instance by reading the given file. 
        
        Arguments:
            filename
                Name of file to read meta-inf from
        """
        
        if not os.path.isfile(filename):
            raise NoManifestFile()
        
        self.__filename = filename
    
    def keys(self):
        """
        Gets the keys in this Manifest() instance. 
        
        Returns:
            A list of keys
        """
        
        keys = set()
        
        for line in fileio.read_file_lines(self.__filename):
            try:
                keys.add(line[:line.index(":")])
            except ValueError:
                pass
        return list(keys)
    
    def has_key(self, key):
        """
        Checks if this Manifest() instance contains a given setting. 
        
        Arguments:
            key
                Key to check
        Returns:
            A boolean
        """
        
        return key in self.keys()
    
    def __contains__(self, key):
        """
        Same as self.has_key(key)
        """
        return self.has_key(key)
        
    def read(self, key):
        """
        Reads a given key from this Manifest() instance or throws aKeyError if 
        it does not exist
        
        Arguments:
            key
                Key to get from this meta-inf instance
        Returns:
            A string representing the value for the given key
        """
        
        the_line_start = "%s:" % (key,)
        
        for line in fileio.read_file_lines(self.__filename):
            if line.startswith(the_line_start):
                return line[line.index(":")+1:].strip()
        
        raise KeyError
    
    def __getitem__(self, key):
        """
        Same as self.get(key)
        """
        return self.read(key)
    
    def write(self, key, value):
        """
        Writes a given key to this Manifest() instance. 
        
        Arguments:
            key
                Key of setting to write
            value
                Value to set this setting to
        Returns:
            A boolean indicating if the write operation was successfull
        """
        
        lines = list(fileio.read_file_lines(self.__filename))
        
        the_line_start = "%s:" % (key,)
        the_line = '%s: %s' % (key, value)
        
        for (i, line) in enumerate(lines):
            if line.startswith(the_line_start):
                lines[i] = the_line
                break
        else:
            lines.append(the_line)
        
        return fileio.write_file_lines(self.__filename, lines)
    
    def __setitem__(self, key, value):
        """
        Same as self.write(key, value)
        """
        return self.write(key, value)
    
    def remove(self, key):
        """
        Removes a line with the given key from the MANIFEST.MF file
        """
        
        the_line_start = "%s:" % (key,)
        
        lines = list(filter(
            lambda l: not l.startswith(the_line_start), 
            fileio.read_file_lines(self.__filename)
        ))
        
        return fileio.write_file_lines(lines)
    
    def __delitem__(self, key):
        """
        Same as self.remove(key)
        """
        return self.remove(key)

class NoManifestFile(exceptions.LMHException):
    def __init__(self):
        super(NoManifestFile, self).__init__('Specefied repository does not have a ManifestFile')