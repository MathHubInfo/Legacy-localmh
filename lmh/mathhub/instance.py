from lmh.mathhub.resolvers import local, remote

class MathHubInstance(object):
    """
    Represents a single MathHub instance that has a local folder where
    repositories can be installed.
    """

    def __init__(self, local_resolver, remote_resolver):
        """
        Creates a new MathHubInstance().

        Arguments:
            local_resolver
                A LocalMathHubResolver() instance used to resolve local MathHub
                respositories.
            remote_resolver
                A RemoteMathHubResolver() instance used to resolve remote
                MathHub respositories.
        """

        if not isinstance(local_resolver, local.LocalMathHubResolver):
            raise TypeError('local_resolver needs to be an instance of local.LocalMathHubResolver')

        if not isinstance(remote_resolver, remote.RemoteMathHubResolver):
            raise TypeError('remote_resolver needs to be an instance of remote.RemoteMathHubResolver')

        self.__local_resolver = local_resolver
        self.__remote_resolver = remote_resolver
