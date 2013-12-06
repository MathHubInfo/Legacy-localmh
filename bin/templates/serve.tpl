// This is an MMT script that builds this project. It can be run by checking out MMT at https://svn.kwarc.info/repos/MMT/deploy and running MMT using the shell scripts given there.

log console
log file build.log
//log+ presenter
//log+ backend
//log+ controller
//log+ extman
//log+ reader
log+ archive    
//log+ checker
//log+ object-checker
//log+ query
//log+ catalog
log+ server
log+ planetary
//log+ uom
//log+ abox
//log+ structure-parser
//log+ parser
//log+ scanner
//log+ lf


extension info.kwarc.mmt.planetary.PlanetaryPlugin
extension info.kwarc.mmt.stex.STeXImporter

archive add .

mathpath fs http://cds.omdoc.org/styles {2}/ext/MMT/styles
base http://docs.omdoc.org/{0}/{1}

server on 8081