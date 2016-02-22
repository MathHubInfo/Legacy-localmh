from lmh.mathhub.resolvers import resolver
from lmh.utils import exceptions

from lmh.external.programs import git
from functools import lru_cache


from urllib.request import urlopen
import lxml.html

from lmh.utils.clsutils.caseclass import caseclass

@caseclass
class RemoteMathHubResolver(resolver.MathHubResolver):
    """
    Represents a MathHubResolver() that can resolve (git) repositories from a
    remote github or gitlab server.
    """
    
    def __init__(self, git_program):
        """
        Creates a new RemoteMathHubResolver() instance.

        Arguments:
            git
                Git() instance that is used to interface with git
        """
        if not isinstance(git_program, git.Git):
            raise TypeError("git_program needs to be a git.Git() instance. ")

        self.git = git_program

    
    def get_repo_path(self, group, name):
        """
        Gets the remote for a single remote repository or throws RepositoryNotFound().
        Should be overriden by the subclass.

        Arguments:
            group
                The name of the group to find the repository.
            name
                Name of the repository to find.
        Returns:
                A String representing the git remote for the repository.
        """

        raise NotImplementedError
    

class GitLabResolver(RemoteMathHubResolver):
    """
    Represents a RemoteMathHubResolver() that checks a remote GitLab instance.
    """
    def __init__(self, git_program, hostname):
        """
        Creates a new GitLabResolver() instance.

        Arguments:
            git_program
                Git() instance that is used to interface with git
            hostname
                HOSTNAME of the GitLab instance
        """

        super(GitLabResolver, self).__init__(git_program)

        self.__hostname = hostname
        self.__repos = None
    
    def can_answer_for(self, name):
        """
        If this function returns True that means this resolver can answer queries
        for the given instance name. For all other cases the behaviour is 
        unspecefied. 
        
        Arguments:
            name
                Name to check against
        Returns:
            A boolean indicating if this instance matches or not
        """
        
        return name == self.hostname

    def get_repo_path(self, group, name):
        """
        Gets the remote for a single remote repository or throws RepositoryNotFound().
        Should be overriden by the subclass.
        """

        https_url = 'https://%s/%s/%s.git' % (self.__hostname, group, name)
        git_url = 'git@%s:%s/%s.git' % (self.__hostname, group, name)

        if self.git.exists_remote(git_url):
            return git_url
        elif self.git.exists_remote(https_url):
            return https_url
        else:
            raise resolver.RepositoryNotFound()
    
    def get_all_repos(self):
        """
        Gets a (cached) list of repositories or throws NotImplementedError
        if not available.

        Returns:
            A list of pairs of strings (group, name) representing repositories.
        """
        
        if self.__repos != None:
            return self.__repos

        base_url = "http://%s/public/" % self.__hostname
        projects_per_page = 20
        repositories = set()

        for i in range(1, 100):
            try:
                response = urlopen('%s?page=%s' % (base_url, i))
                response = response.read()

            except Exception as e:
                raise NetworkingError()

            try:
                # parse the html
                project_list_page = lxml.html.fromstring(response)

                # find all <a class='project'> .hrefs
                new_projects = project_list_page.xpath("//a[@class='project']/@href")

                # and remove the starting /s
                new_projects = list(map(lambda s:s[1:].split("/") if s.startswith("/") else s.split("/"), new_projects))

                # if we have fewer projects then the max, we can exit now
                if len(new_projects) < projects_per_page:
                    break

                repositories.update([(p[0], p[1]) for p in new_projects])

            except Exception as e:
                raise NetworkingError()
        
        self.__repos = list(sorted(repositories))
        return self.__repos
    
    def repo_exists(self, group, name):
        """
        Checks if this Resolver can find the path to a repository. By default checks the output
        of get_all_repos() and then falls back to get_repo_path().  
        
        Arguments: 
            group
                Name of the group to check for repo. 
            name
                Name of the repository to check. 
        Returns:
            A boolean indicating if the repository exists or not. 
        """
        
        try:
            if self.__repos != None:
                all_repos = self.get_all_repos()
            
                if (group, name) in all_repos:
                    return True
        except exceptions.MathHubException:
            pass
        
        try:
            self.get_repo_path(group, name)
            return True
        except exceptions.MathHubException:
            return False

class NetworkingError(exceptions.MathHubException):
    """
    Exception that is thrown when a networking error occurs.
    """
    def __init__(self):
        super(NetworkingError, self).__init__('Unable to establish connection. ')
