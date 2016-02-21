__encodings__ = ['utf8', 'latin-1']

def read_file(filename):
    """
    Reads text from a file on disk. 
    
    Arguments:
        filename
            Name of file to read
    Returns:
        A string representing the file content or None if reading failed
    """
    
    for enc in __encodings__:
        try:
            with open(filename, "r", encoding=enc) as text_file:
                content = text_file.read()
            
            return content
        except UnicodeDecodeError:
            pass
        except:
            return None

def read_file_lines(filename):
    """
    Same as read_file except reads file lines and returns a list of strings. 
    
    Arguments:
        filename
            Name of file to read
    Returns:
        A list of lines in the file
    """
    
    for enc in __encodings__:
        try:
            with open(filename, "r", encoding=enc) as text_file:
                content = text_file.readlines()
            
            return content
        except UnicodeDecodeError:
            pass
        except:
            return None

def write_file(filename, text):
    """
    Writes text to a file on disk. 
    
    Arguments:
        filename
            Name of file to write
        text
            String representing text to be written to disk
    Returns:
        A boolean indicating if the write operation was successfull
    """
    
    if isinstance(text, list):
        text = '\n'.join(text)
    
    try:
        with open(filename, 'w', encoding=__encodings__[0]) as text_file:
            text_file.write(text)
    except:
        return False
    
    return True