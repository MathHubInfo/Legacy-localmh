// This is an MMT script that builds this project. It can be run by checking out MMT at https://svn.kwarc.info/repos/MMT/deploy and running MMT using the shell scripts given there.

log console
log file build.log
//log+ presenter
//log+ backend
//log+ controller
//log+ extman
//log+ reader
log+ archive 
log+ steximporter
//log+ checker
//log+ object-checker
//log+ query
//log+ catalog
//log+ server
//log+ uom
//log+ abox
//log+ structure-parser
//log+ parser
//log+ scanner
//log+ lf

extension info.kwarc.mmt.planetary.PlanetaryPlugin
extension info.kwarc.mmt.stex.STeXImporter

archive add .

build {1} stex-omdoc
build {1} index
build {1} mws-content
build {1} mws-narration

exit
