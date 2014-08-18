# LocalMH has been moved go github.

[Please click here to use the current version. ](https://github.com/KWARC/localmh)

Please only use the current version.
This page is mainted only for backward-compatibility and may be shut down at any time.

# LocalMH

LocalMH is an infrastructure for local (in a working tree) management of the content in http://MathHub.info.

The infrastructure consists of set of resources (Makefiles, LaTeX Packages, LaTeXML, sTeX) and a management tool lmh.

## Installation

There are several ways to install lmh. The easiest way is:

```bash
pip install lmh
lmh core --install
```

Note that the pip baased installation might require python development tools to be installed
(package python-dev on Ubuntu / Debian).

This will clone lmh from http://gl.mathhub.info/MathHub/localmh. To manually install lmh, simply installed the dependencies and then clone lmh to a directory of your choice. Then add the subdirectory bin to your $PATH.

Once lmh is installed, you will have to run

```bash
lmh setup --install
```

for lmh to install and configure run-time dependencies correctly.

### Upgrade

To upgrade only lmh itself run:

```bash
lmh selfupdate
```

Note that this will not automatically update dependencies. To update dependencies, run:

```bash
pip install --upgrade lmh
```

### Dependencies

Currently only *nix-based systems are supported.

#### Installer dependencies

The installer requires the following programs installed to function properly. Whenever possible the installer will warn if these are missing:

* pip
* git

#### Runtime dependencies

In addition to the installer dependencies the following are required for lmh to run properly:

* svn
* pdflatex, preferably TexLive 2013 or newer
* perl with cpanminus installed
* libxml2
* libxslt

### System-specific instructions

#### Ubuntu / Debian

On newer Ubuntu / Debian systems, all required packages may be installed with the following command:

```bash
sudo apt-get install python python-pip python-dev subversion git texlive cpanminus libxml2-dev libxslt-dev libgdbm-dev
```

Then you can install lmh normally using:

```bash
pip install lmh # May require sudo
lmh core --install
lmh setup --install
```



#### Windows

On Windows, dependencies are more difficult to install.

**
    This has been tested to the minimum and may not work at all on your system.
    Windows support is experimental. Whenever possible, try to use either Linux
    or Mac OS for lmh.
**

Even if 64bit versions are available, try to install 32 bit versions as otherwise some compatibility issues can occur.

1) Install [Python](https://www.python.org/download/) 2.7. Make sure to select "Add Python.exe to PATH".

2) Install a version of Visual Studio, preferably [Visual Studio 2010 C++ Express](http://www.visualstudio.com/downloads/download-visual-studio-vs#d-2010-express). (Note: This step may take a while depending on the speed of your network connection. )

3) Install [Git](http://git-scm.com/download/win).

4) Open the "Git bash" (with administrator rights) and install pip:

```
easy_install pip
```

5) Now  download the lmh installer:

```
pip install lmh
```

If this fails and complains about not being unable to find "vcvarsall.bat",
you will have to make sure that the environment variable "VS90COMNTOOLS" is set
correctly. If you check your environment variables there should already be a
variable like VS100COMNTOOLS there, use the value of that one. The error occurs
because Visual Studio is installed in the wrong version (or not at all). Please
also refer to
[this thread](http://stackoverflow.com/questions/17658092/unable-to-find-vcvarsall-bat-using-python-3-3-in-windows-8).

6) Now you should be able to run:

```
lmh core --install
```
to install lmh. Now we are ready to install all the runtime dependencies.

7) Install Subversion. If you also want a GUI client, you can use [TortoiseSVN](http://tortoisesvn.net/). Make sure the executables are added to the $PATH environment variable. ("Install Command Line Tools" option in the trotoise svn installer. )
(You can check this by opening a prompt and typing svn which should ouput something like "Type 'svn help' for usage. " )

8) Install [TexLive](https://www.tug.org/texlive/). This should install both "pdflatex" and "perl" executables. ** Depending on your network speed, this might take some time. **

9) Install [Strawberry Perl](http://strawberryperl.com/). This will setup cpanminus as well.

10) Download [GNU Make](http://gnuwin32.sourceforge.net/packages/make.htm) and put it in your $PATH. You should be able to run "make" from the command line without getting any errors.

11) Download [GNU tar](http://gnuwin32.sourceforge.net/packages/gtar.htm) and put it in your $PATH. This will provide the tar executable.

For Make and Tar, If you use the automated installer, make sure to add "C:\Program Files (x86)\GnuWin32\bin" to the PATH.

12) Now you should be able to run

```
lmh setup --install
```

**NOTICE: ** Currently anything that needs cpanm needs to be installed manually on Windows as installation fails.

13) You are ready to use lmh.

## Directory Structure

Resources/directory structure:

* MathHub:		stored offline content from MathHub.info
* bin:			main scripts, auto-added to $PATH via the pip package
* docs:			Documentation, autogenerated
* lmh:			main source directory for lmh
* ext:			external Software
* sty:			LaTeX packages used in MathHub.info
* logs:			crash reports that will help developers improve lmh.
* styles:		for the notation definitions MMT uses for generating XHTML from OMDoc
* pip-package:	A pip package which serves as an installer for lmh

## License

GPL, version 3.0

For the full license text, please see [gpl-3.0.txt](gpl-3.0.txt).
