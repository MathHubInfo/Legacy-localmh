from typing import List


class FileIO(object):
    """Contains all File Input / Output functionality"""

    encodings = ['utf8', 'latin-1']  # type: List[str]

    @staticmethod
    def read_file(filename: str) -> str:
        """ Reads text from a file on disk.

        :param filename: Name of file to read.
        :return:  A string representing the file content or None if reading
        failed.
        """

        for enc in FileIO.encodings:
            try:
                with open(filename, "r", encoding=enc) as text_file:
                    content = text_file.read()

                return content
            except UnicodeDecodeError:
                pass
            except IOError:
                return None

    @staticmethod
    def read_file_lines(filename: str) -> List[str]:
        """ Same as read_file except that it reads file lines and returns a
        list of strings.

        :param filename: Name of file to read.
        :return: A list of lines in the file.
        """

        for enc in FileIO.encodings:
            try:
                with open(filename, "r", encoding=enc) as text_file:
                    content = text_file.readlines()

                return [c[:-1] if c.endswith("\n") else c for c in content]
            except UnicodeDecodeError:
                pass
            except IOError:
                return None

    @staticmethod
    def write_file(filename: str, text: str) -> bool:
        """ Writes text to a file on disk.

        :param filename: Name of file to write
        :param text: String representing text to be written to disk
        :return: A boolean indicating if the write operation was successful
        """

        if isinstance(text, list):
            text = '\n'.join(text)

        try:
            with open(filename, 'w', encoding=FileIO.encodings[0]) as text_file:
                text_file.write(text)
        except IOError:
            return False

        return True

    @staticmethod
    def write_file_lines(filename: str, lines: List[str]) -> bool:
        """ Same as write_file() except that it takes a list of lines instead.

        :param filename:
        :param lines:
        :return: A boolean indicating if the write operation was successful
        """

        return FileIO.write_file(filename, '\n'.join(lines))

__all__ = ["FileIO"]
