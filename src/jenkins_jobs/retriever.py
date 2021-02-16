"""Retrieve Jenkins jobs information"""
import shelve
from abc import ABC, abstractmethod
import xmltodict
import jenkins

from jenkins_jobs.jobs import PipelineJob, MavenJob, FreestyleJob, PluginBasedJob


class Retriever(ABC):

    plugin_based_jobs = {
        'workflow-job': PipelineJob,
        'maven-plugin': MavenJob
    }

    @abstractmethod
    def all_jobs():
        pass

    def _job_builder(self, name, config):

        try:
            if 'project' in config['definition']:
                # not a plugin, because FreestyleJob doesn't use one
                return FreestyleJob(name, config)
            else:
                plugin = PluginBasedJob.plugin(config)
                try:
                    return self.plugin_based_jobs[plugin](name, config)
                except KeyError as e:
                    raise Exception('Unknown job type "{}"'.format(e))
        except KeyError as e:
            msg = 'Unexpected data, missing {} root key in data structure'
            print(msg.format(e))


class FileSystemRetriever(Retriever):
    """."""

    def __init__(self, shelve_file_path):
        self.shelf = shelve.open(shelve_file_path, flag='r')

    def all_jobs(self):

        def gen_jobs():
            for job_name in self.shelf:
                yield self._job_builder(job_name, self.shelf[job_name])

        return gen_jobs


class RESTRetriever(Retriever):

    def __init__(self, user, token, jenkins_server):
        self.server = jenkins.Jenkins(jenkins_server, username=user,
                                      password=token)

    def all_jobs(self):

        def gen_jobs():
            for job in self.server.get_jobs():
                raw_data = self.server.get_job_config(job['name'])
                yield self._job_builder(job['name'], xmltodict.parse(raw_data))

        return gen_jobs
