# LocalMH

LocalMH is an infrastructure for local (in a working tree) management of the content in http://mathhub.info.

## Install

Currently, the only supported way to install localmh is to use [localmh_docker](https://github.com/KWARC/localmh_docker).
You need Python 3.5+ in order to run this tool.

## Documentation

Basic Instructions on how to use lmh can be found at [http://mathhub.info/help/offline-authoring](http://mathhub.info/help/offline-authoring).

New documentation (still in development) can be found under docs/. It can be generated with [MkDocs](http://www.mkdocs.org/).

## Directory Structure

LMH is split up into serveral directories:
* Source Directories: Used for source code and other core files.
  * bin:      contains template and main script
  * lmh:			main source directory for lmh
  * docs:			Documentation (work in progess)
  * sty:      LaTeX packages used in MathHub.info
  * styles:		for the notation definitions MMT uses for generating XHTML from OMDoc
* Data Directories: Used for user-generated content and other Data
  * MathHub:  stored offline content from MathHub.info
  * ext:      external Software (that is installed automatically)
  * logs:			crash reports that will help developers improve lmh.

## License

GPL, version 3.0

For the full license text, please see [gpl-3.0.txt](gpl-3.0.txt).

## Documentation + Code Standard (for developers)
* Documentation standard
    * every function gets type annotations according to PEP484
        * every argument should get a type annotation
            * may be omitted if it would create circular imports
                * in that case it must be documented in the docstring
        * the return type should also be annotated
            * may be omitted for constructors
            * may be omitted if it would create circular imports
                * in that case it must be documented in the docstring
    * every function + class must have a docstring
        * there should be a blank line between the description and the parameters
        * each parameter should get a human readable description
            * self may be omitted
        * the return value should get a description if it is not clear from the description
    * every class attribute should get a PEP484 type annotation via ```# type: something```
    * every documentation string should end with a dot
    * after a docstring there should be a new line
* Code Standard
    * we should conform to PEP8
    * **NEVER** access private members outside of their class
        * turn them into a property instead
    * use underscores for file and method names, CamelCase for class names
    * do not use standalone functions, use ```@staticmethod``` instead
    * try to import at specific as possible
        * **Do not** use ```from module import *``` without an ```__all__``` in
        the imported module.
        * whenever possible, add an ```__all__``` at then end of a module
    * avoiding circular imports with Managers
        * The Manager imports the object in the last line
        * The Objects import the manager normally
        * The __init__.py in the appropriate package imports both and then loads the manager

Example:
```python
class Example(object):
    """ An example class. """

    def __init__(self, name : str):
        """ Creates a new Example instance.

        :param name: The name of this object.
        """

        self.name = name # type: str

        self.__secret = 16 # type: int

    @property
    def secret(self) -> int:
        """ Returns the secret contained in this example. """

        return self.__secret
```
