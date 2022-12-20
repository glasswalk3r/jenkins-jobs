"""Classes to retrieve Jenkins jobs information."""

import shelve
from abc import ABC, abstractmethod
import xmltodict
import jenkins

from jenkins_jobs.jobs import (
        PipelineJob,
        MavenJob,
        FreestyleJob,
        PluginBasedJob
)
from jenkins_jobs.exceptions import UnknownJobTypeError, InvalidXMLConfigError


class Retriever(ABC):
    """Base class for a job retriever."""

    plugin_based_jobs = {
        'workflow-job': PipelineJob,
        'maven-plugin': MavenJob
    }

    @abstractmethod
    def all_jobs():
        """Return a generator for all the jobs.

        No parameter is expected.

        :return: a generator to be iterator over
        :rtype: function
        """
        pass  # pragma: no cover

    @classmethod
    def _job_builder(cls, name, config):
        """Create a instance of a job depending on it's type.

        This is a factory method.

        :param str name: the of the job
        :param dict config: the job configuration

        :return: a job instance
        :rtype: JenkinsJob
        """

        try:
            if 'project' in config:
                # not a plugin, because FreestyleJob doesn't use one
                return FreestyleJob(name, config)
            else:
                plugin = PluginBasedJob.plugin(config)
                try:
                    return cls.plugin_based_jobs[plugin](name, config)
                except KeyError as e:
                    raise UnknownJobTypeError(str(e))
        except KeyError as e:
            raise InvalidXMLConfigError(str(e))


class FileSystemRetriever(Retriever):
    """File system based retriever of Jenkins jobs.

    This class is particulary useful to cache results for faster local
    testing.
    """

    def __init__(self, shelve_file_path):
        """Initialize the instance.

        :param str shelve_file_path: the complete path to a Python shelve file

        :return: Nothing
        :rtype: None
        """
        self.shelf = shelve.open(
                shelve_file_path, flag='r')  # pragma: no cover

    def all_jobs(self):
        """Implement parent abstract method."""

        def gen_jobs():
            for job_name in self.shelf:
                yield self._job_builder(job_name, self.shelf[job_name])

        return gen_jobs


class RESTRetriever(Retriever):
    """REST based retriever for Jenkins jobs."""

    def __init__(self, user, token, jenkins_server):
        """Initialize the instance.

        :param str user: the Jenkins user for REST API authentication
        :param str token: the Jenkins user's token for REST API authentication
        :param str jenkins_server: the URL to the Jenkins server

        :return: Nothing
        :rtype: None
        """
        self.server = jenkins.Jenkins(jenkins_server, username=user,
                                      password=token)  # pragma: no cover

    def all_jobs(self):
        """Implement parent abstract method."""

        def gen_jobs():
            for job in self.server.get_jobs():
                raw_data = self.server.get_job_config(job['name'])
                yield self._job_builder(job['name'], xmltodict.parse(raw_data))

        return gen_jobs
