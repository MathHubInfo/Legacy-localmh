from typing import List, Tuple, Optional
from urllib.request import urlopen

import lxml.html

from lmh.programs.git import Git

from lmh.mathhub.resolvers import resolver
from lmh.utils import exceptions


class RemoteMathHubResolver(resolver.MathHubResolver):
    """ Represents a MathHubResolver() that can resolve (git) repositories from a remote GitHub or GitLab server. """
    
    def __init__(self, git: Git):
        """ Creates a new RemoteMathHubResolver() instance.

        :param git: Git() instance that is used to interface with git
        """

        self.__git = git  # type: Git

    @property
    def git(self) -> Git:
        """ Returns the Git program used by this RemoteMathHubResolver(). """
        return self.__git

    def get_repo_path(self, group: str, name: str) -> str:
        """ Gets the full path to a repository or throws NotImplementedError. May also throw RepositoryNotFound. Should
        be overridden by the subclass.

        :param group: Group of repository to resolve.
        :param name: Name of repository to resolve.
        """

        raise NotImplementedError

    def get_all_repos(self) -> List[Tuple[str, str]]:
        """ Gets a (possibly cached) list of repositories or throws NotImplementedError if not available. Should be
        overridden by the subclass.

        :return: A list of pairs of strings (group, name) representing repositories.
        """

        raise NotImplementedError

    def clear_repo_cache(self) -> None:
        """ Clears the cache of this Resolver. Should be implemented by the subclass. """

        raise NotImplementedError


class GitLabResolver(RemoteMathHubResolver):
    """ Represents a RemoteMathHubResolver() that checks a remote GitLab instance. """

    def __init__(self, git: Git, hostname: str):
        """ Creates a new GitLabResolver() instance.

        :param git: Git() instance that is used to interface with git.
        :param hostname: HOSTNAME of the GitLab instance
        """

        super(GitLabResolver, self).__init__(git)

        self.__hostname = hostname  # type: str
        self.__repos = None  # type: Optional[List[str]]

    @property
    def hostname(self) -> str:
        """ Returns the hostname used by this GitLab resolver. """

        return self.__hostname
    
    def can_answer_for(self, name: str) -> bool:
        """ Performs a partial check if this resolver can answer queries for the given instance name. If this method
        returns true, the MathHubResolver can answer queries, for all other cases the behaviour is unspecified. By
        default returns False, so it should be overridden in a subclass.

        :param name: Name to check
        """
        
        return name == self.hostname

    def get_repo_path(self, group: str, name: str) -> str:
        """ Gets the remote for a single remote repository or throws RepositoryNotFound().

        :param group: Group of repository to resolve.
        :param name: Name of repository to resolve.
        """

        https_url = 'https://%s/%s/%s.git' % (self.hostname, group, name)
        git_url = 'git@%s:%s/%s.git' % (self.hostname, group, name)

        if self.git.exists_remote(git_url):
            return git_url
        elif self.git.exists_remote(https_url):
            return https_url
        else:
            raise resolver.RepositoryNotFound()
    
    def get_all_repos(self) -> List[Tuple[str, str]]:
        """ Gets a (possibly cached) list of repositories or throws NotImplementedError if not available.

        :return: A list of pairs of strings (group, name) representing repositories.
        """

        # Fill the cache
        if self.__repos is None:
            self.__repos = self._get_all_repos()

        # and return it
        return self.__repos

    def clear_repo_cache(self) -> None:
        """ Clears the cache of this Resolver. """

        self.__repos = None

    def _get_all_repos(self) -> List[Tuple[str, str]]:
        """ Gets a non-cached list of repositories or throws NotImplementedError if not available.

        :return: A list of pairs of strings (group, name) representing repositories.
        """

        base_url = "http://%s/public/" % self.hostname
        projects_per_page = 20
        repositories = set()

        for i in range(1, 100):
            try:
                response = urlopen('%s?page=%s' % (base_url, i))
                response = response.read()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                raise NetworkingError()

            try:
                # parse the html
                project_list_page = lxml.html.fromstring(response)

                # find all <a class='project'> .hrefs
                new_projects = project_list_page.xpath("//a[@class='project']/@href")

                # and remove the starting /s
                new_projects = list(
                    map(lambda s: s[1:].split("/") if s.startswith("/") else s.split("/"), new_projects))

                # if we have fewer projects then the max, we can exit now
                if len(new_projects) < projects_per_page:
                    break

                repositories.update([(p[0], p[1]) for p in new_projects])
            except KeyboardInterrupt:
                raise
            except Exception as e:
                raise NetworkingError()

        return list(sorted(repositories))
    
    def repo_exists(self, group: str, name: str) -> bool:
        """ Checks if this Resolver can find the path to a repository.

        :param group: Name of the group to check for repo.
        :param name: Name of the repository to check.
        """

        # use the cache of all repos if available
        try:
            if self.__repos is not None:
                all_repos = self.get_all_repos()
            
                if (group, name) in all_repos:
                    return True
        except exceptions.MathHubException:
            pass

        # fallback to checking the git url directory -- maybe it is private and the user needs ssh access
        try:
            self.get_repo_path(group, name)
            return True
        except exceptions.MathHubException:
            return False


class NetworkingError(exceptions.MathHubException):
    """ Exception that is thrown when a networking error occurs. """

    def __init__(self):
        """ Creates a new NetworkingError() instance. """

        super(NetworkingError, self).__init__('Unable to establish connection. ')
