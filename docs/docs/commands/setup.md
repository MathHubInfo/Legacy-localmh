# lmh setup

Lmh setup is responsible for installing and managing external dependencies. The following dependencies are currently managed by lmh setup:

* [LaTeXML](http://dlmf.nist.gov/LaTeXML/)
* [LaTeXMLs](https://github.com/dginev/LaTeXML-Plugin-latexmls)
* [LaTeXMLStomp](https://github.com/KWARC/LaTeXML-Plugin-latexmlstomp)
* [sTeX](https://github.com/KWARC/sTeX)
* [MMT](https://svn.kwarc.info/repos/MMT/doc/html/index.html)

## Modes of lmh setup

Lmh setup works similar to a package manager. It has several modes:

* `--install` to install a package,
* `--update` to update a package,
* `--remove` to uninstall a package and
* `--reset` to reinstall a package.

Each of the modes can be invoked as follows:

```bash
lmh setup --install package_name
```

The package names come from the software managed above. In addition to these there is the `all` package (which installs all software above) and the `self` package. The self package can be used to upgarde lmh itself. See the [lmh selfupgrade](selfupgrade) command.


Packages are installed in the ext/ directory of the localmh installation.

Installing a package consists of cloning the source repository and possibly compiling the program.

Package updates work by ```git pull```ing the source code (or ```svn up```) and then re-running the compilation.

In order to remove a package, the appropriate directory is simply deleted.

To reset a package, it is first removed ant then re-installed.

## Package Sources and Versions

Sometimes a different version of a software is required. To achieve this, the following syntax can be used when installing:

```
lmh setup --install package_name:source@branch
```

Here package_name is the name of the package to be installed, source is the source repository it comes from and branch the desired branch. Both source and branch name can be omitted.

The default sources and branches can be configured with [lmh config](config), specifically via the `setup::latexml::source`, `setup::latexml::branch`, `setup::latexmls::source`, `setup::latexmls::branch`, `setup::latexmlstomp::source`, `setup::latexmlstomp::branch`, `setup::stex::source`, `setup::stex::branch`, `setup::mmt::source` and `setup::mmt::branch` settings.

## Available packages
