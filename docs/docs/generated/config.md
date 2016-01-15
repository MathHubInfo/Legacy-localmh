#List of configuration Settings

This is a list of all configuration settings to be used with [lmh config](../commands/config). 


| Name |  | Type | Default |
| ------------ | ------------- | ------------ | ------------ |
| env::cpanm | Path to the cpanm executable. Auto-detected if empty. | string |  |
| env::git | Path to the Git executable. Auto-detected if empty. | string |  |
| env::java | Path to the java executable. Auto-detected if empty. | string |  |
| env::latexmlc | Path to the latexmlc executable. Auto-detected if empty. | string |  |
| env::pager | A full path to a pager to use for long outputs. If empty, no pager is used. | string |  |
| env::pdflatex | Path to the pdflatex executable. Auto-detected if empty. | string |  |
| env::perl | Path to the perl executable. Auto-detected if empty. | string |  |
| gen::default_workers | Default number of workers to use for generating pdf and omdoc. | int+ | 8 |
| gen::pdf::timeout | Timeout when generating PDFs. In seconds. | int+ | 120 |
| gl::deploy_branch_name | Name for automatically created deploy branches. | string | deploy |
| gl::host | Host for gitlab interaction. Should have a final slash. | string | http://gl.mathhub.info/ |
| gl::issue_url | URL to issues page. | string | https://github.com/KWARC/localmh/issues |
| gl::private_token | Gitlab Private token for gitlab interaction. Leave blank to prompt for username / password. | string |  |
| gl::status_remote_enabled | If set to true, enables lmh status remote checking by default. | bool | False |
| init::allow_nonempty | Allow to run lmh init in non-empty directories. | bool | False |
| install::noglobs | Disable globs when installing repositories. | bool | False |
| install::sources | Url prefixes to clone git repositories from. Seperated by ;s. | string | git@gl.mathhub.info:;http://gl.mathhub.info/ |
| mh::issue_url | URL to issues page for each repository. | string | https://gl.mathhub.info/$name/issues |
| self::colors | Use colors in the output. | bool | False |
| setup::cpanm::selfcontained | Use self-contained local CPANM repositories. | bool | True |
| setup::latexml::branch | Default branch for latexml. Automatically uses the remote HEAD if undefined. | string |  |
| setup::latexml::source | Default Source for latexml. | string | https://github.com/KWARC/LaTeXML.git |
| setup::latexmls::branch | Default branch for latexmls. Automatically uses the remote HEAD if undefined. | string |  |
| setup::latexmls::source | Default Source for latexmls. | string | https://github.com/dginev/LaTeXML-Plugin-latexmls |
| setup::latexmlstomp::branch | Default branch for latexmlstomp. Automatically uses the remote HEAD if undefined. | string |  |
| setup::latexmlstomp::source | Default Source for latexmlstomp. | string | https://github.com/KWARC/LaTeXML-Plugin-latexmlstomp.git |
| setup::mmt::branch | Default branch for MMT. Automatically uses gh-pages if empty. | string | gh-pages |
| setup::mmt::source | Default Source for MMT. | string | https://github.com/KWARC/MMT.git |
| setup::stex::branch | Default branch for sTeX. Automatically uses the remote HEAD if undefined. | string |  |
| setup::stex::source | Default Source for sTeX. | string | https://github.com/KWARC/sTeX.git |
