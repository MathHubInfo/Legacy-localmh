# New code to be implemented

Repository
  subclass ClonedRepository
  subclass RemoteRepository

Repository
  .is_installed(self) -> Boolean

  .getRemote(self) -> RemoteRepository
  .getClone(self) -> ClonedRepository

LocalRepository
  .toPath(self, absolute = False) -> string
  .toTriple(self) -> (String, String, String)

  .getModules(self) -> List[Module]
  .locate(self, names) -> Module

RemoteRepository
  .install(self) -> Option[ClonedRepository]
