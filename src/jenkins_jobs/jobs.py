"""Main module."""

from collections import deque
from abc import ABC, abstractmethod

from jenkins_jobs.exceptions import MissingXMLElementError


class JenkinsJob(ABC):
    timer_trigger_node = 'hudson.triggers.TimerTrigger'

    def __init__(self, name, config):
        self.name = name
        self.timer_trigger_based = False
        self.timer_trigger_spec = None
        self._onliner(config)
        self._find_desc(config)
        self._find_timer_trigger(config)

    @abstractmethod
    def _find_desc(self, config):
        pass  # pragma: no cover

    @abstractmethod
    def _find_timer_trigger(self, config):
        pass  # pragma: no cover

    def _onliner(self, config):
        description = self._find_desc(config)

        if description:
            description = description.replace('\r\n', '\n')
            lines = description.lstrip().rstrip().split('\n')
            new_lines = deque()

            for line in lines:
                if line == '':
                    continue

                new_lines.append(line)

            self.description = ' '.join(new_lines)
        else:
            self.description = '*** MISSING DESCRIPTION ***'

    @staticmethod
    def _clean_spec(timer_spec):
        spec = None

        if timer_spec is None:
            return spec

        clean_lines = deque()
        normalized = timer_spec.replace('\r\n', '\n')
        lines = normalized.split('\n')

        for line in lines:
            if line.startswith('#') or line == '':
                continue
            else:
                clean_lines.append(line)

        return '\n'.join(clean_lines)

    def __str__(self):
        if self.timer_trigger_based:
            return '|'.join([
                self.name,
                self.__class__.__name__,
                self.description,
                str(self.timer_trigger_based),
                self.timer_trigger_spec
            ])
        else:
            return '|'.join([
                self.name,
                self.__class__.__name__,
                self.description,
                str(self.timer_trigger_based),
                'not applicable'
            ])


class PluginBasedJob(JenkinsJob):
    root_node = None

    @staticmethod
    def _plugin_type(config):
        # <flow-definition plugin="workflow-job@2.36">
        try:
            element = next(iter(config))
        except StopIteration:
            element = None

        return element

    @staticmethod
    def plugin(config):
        plugin_type = PluginBasedJob._plugin_type(config)
        plugin = config[plugin_type]['@plugin']
        # plugin have their version include must of the times
        return plugin.split('@')[0].lower()

    def _find_desc(self, config):
        plugin_type = PluginBasedJob._plugin_type(config)
        return config[plugin_type]['description']


class PipelineJob(PluginBasedJob):
    root_node = 'flow-definition'
    trigger_grandparent_node = 'org.jenkinsci.plugins.workflow.job.properties.Pipeline\
TriggersJobProperty'

    def _find_timer_trigger(self, config):
        try:
            tmp = config[self.root_node]['properties']

            if self.trigger_grandparent_node in tmp:
                tmp = tmp[self.trigger_grandparent_node]

                if tmp and 'triggers' in tmp:
                    tmp = tmp['triggers']

                    if tmp and self.timer_trigger_node in tmp:
                        self.timer_trigger_spec = self._clean_spec(
                            tmp[self.timer_trigger_node]['spec'])
                        # yes, there might be a existing node with nothing
                        # defined
                        if self.timer_trigger_spec:
                            self.timer_trigger_based = True
        except KeyError as e:
            raise MissingXMLElementError(element=str(e), job_name=self.name, context='a timer trigger')


class MavenJob(PluginBasedJob):
    root_node = 'maven2-moduleset'
    trigger_parent_node = 'triggers'

    def _find_timer_trigger(self, config):
        try:
            tmp = config[self.root_node]

            if self.trigger_parent_node in tmp:
                tmp = tmp[self.trigger_parent_node]

                if tmp and self.timer_trigger_node in tmp:
                    self.timer_trigger_spec = self._clean_spec(
                        tmp[self.timer_trigger_node]['spec'])
                    # yes, there might be a existing node with nothing
                    # defined
                    if self.timer_trigger_spec:
                        self.timer_trigger_based = True
        except KeyError as e:
            raise MissingXMLElementError(element=str(e), job_name=self.name, context='a timer trigger')


class FreestyleJob(JenkinsJob):
    root_node = 'project'

    def _find_desc(self, config):
        try:
            return config[self.root_node]['description']
        except KeyError as e:
            raise MissingXMLElementError(element=str(e), job_name=self.name, context='the job description')

        return None

    def _find_timer_trigger(self, config):
        try:
            tmp = config[self.root_node]['triggers']

            # tmp will be None if there is not trigger at all
            if tmp and self.timer_trigger_node in tmp:
                self.timer_trigger_spec = self._clean_spec(
                    tmp[self.timer_trigger_node]['spec'])
                # yes, there might be a existing node with nothing defined
                if self.timer_trigger_spec:
                    self.timer_trigger_based = True
        except KeyError as e:
            raise MissingXMLElementError(element=str(e), job_name=self.name, context='a timer trigger')
