# Manual Installation

<div class="alert alert-success" role="alert">
Usually lmh should be installed via <a href="https://github.com/KWARC/localmh_docker">localmh_docker</a> only. Check the appropriate documentation there.
</div>

A manual installation works in 3 steps:

1. Install dependencies
2. Clone this repository and make the ```lmh``` script available in your $PATH
3. Run automatic setup scripts.

Manual installation is only supported on Linux and Mac based system.

## Installing dependencies

In order for localmh to function properly several dependencies are needed. These should be installed first:

* [Python 2.7](https://www.python.org/), python3 may or may not work
* [pip](https://pip.pypa.io/en/stable/) a python packaage manager, so we can install some python packages

* [Perl](https://www.perl.org/) in order to run LaTeXML
* [cpanminus](http://search.cpan.org/~miyagawa/App-cpanminus-1.7037/lib/App/cpanminus.pm) to install perl packages needed for LaTeXML

* [TexLive 2014](https://www.tug.org/texlive/) or later, needed by LaTeXML and to make pdfs.
* [Java](https://java.com/) to be able to run MMT


* [git](https://git-scm.com/) to install localmh and MathHub repositories.
* [svn](https://subversion.apache.org/) needed to install MMT

* libxml2, libxslt and libssl development headers. Needed for LaTeXML to install properly.

On a clean Debian or Ubuntu based system all the dependencies may be installed with the following command:

```bash
apt-get install python python-dev python-pip git subversion tar fontconfig cpanminus libxml2-dev libxslt-dev libssl-dev libgdbm-dev openjdk-7-jre-headless textlive-full perl
```

Next we need to install some of the required python modules:

```bash
pip install beautifulsoup4 psutil pyapi-gitlab
```

## Cloning Lmh
The next step is to clone lmh somewhere and symlink the ```lmh``` script into the $PATH variable.

First choose a directory and clone localmh there:

```bash
git clone https://github.com/KWARC/localmh $HOME/localmh
```

Next, we need to symlink the lmh script into the $PATH. In this command we assume that /usr/local/bin exists and is included in $PATH:

```bash
ln -s $HOME/localmh/bin/lmh /usr/local/bin/lmh #May required sudo
```

## Running setup scripts

Next, we need to install a lot of required packages. Assuming all the dependencies are installed correctly, this can be done with the following command:
```bash
lmh setup --no-firstrun --install all
```

That's it. After this lmh should be installed and ready for use. See [Getting started with lmh](getting_started) for some basic commands.
