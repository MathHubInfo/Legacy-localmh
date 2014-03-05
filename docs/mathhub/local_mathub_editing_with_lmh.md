lmh is a tool for managing a set of MathHub repositories and their dependencies. lmh is open source, the  repository is at [http://gl.mathhub.info/admin/projects/MathHub/localmh](http://gl.mathhub.info/MathHub/localmh). The initial version has been realized as a Python script by [Constantin Jucovschi](http://kwarc.info/people/cjucovschi/) implementing specifications of [Michael Kohlhase](http://kwarc.info/kohlhase/). lmh is a command-line utility that adds an abstraction layer for local editing workflows over GIT commands based on the particular layout of MathHub repositories. 

lmh commands look like this:

```
lmh action [options]
```
Valid actions are:

```
    about     shows version and general information.
    find      find tool
    status    shows the working tree status of repositories
    log       shows recent commits in all repositories
    install   fetches a MathHub repository and its dependencies
    setup     sets up local math hub and fetches external requirements
    shell     launch a shell with everything set to run build commands.
    xhtml     generate XHTML
    init      initialize repository with MathHub repository structure
    commit    commits all changed files
    push      send changes to mathhub
    update    get repository and tool updates
    gen       updates generated content
    clean     clean repositories of generated files
    git       run git command on multiple repositories
    depcrawl  crawls current repository for dependencies
    checkpaths
              check paths for validity
    repos     prints the group/repository of the current Math Hub repository
    root      prints the root directory of the Local Math Hub repository
    sms       generates sms files, alias for lmh gen --sms
    omdoc     generates omdoc files, alias for lmh gen --omdoc
    pdf       generates pdf files, alias for lmh gen --pdf
```

most actions are sensitive to the local directory and restrict them to that. The option -h gives help, in particular, lmh -h generates a current version of the documentation in the table above. 

The recommended way of installing lmh is to run: 

```bash
pip install lmh # This may require admin rights
lmh setup # This will download and install lmh into $HOME/localmh
```

This requires pip to be installed on the system. 

For more information on how to install and use lmh, see [http://mathhub.info/help/lmh-workflows](http://mathhub.info/help/lmh-workflows). 