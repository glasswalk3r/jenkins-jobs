"""Main module."""

from collections import deque
from abc import ABC, abstractmethod

from jenkins_jobs.exceptions import (
        MissingXMLElementError,
        InvalidFindTimerTriggerError
)


class TimerTriggerResult():
    """Representation of a timer trigger search.

    A instance of this class must be returned by implementations of the
    abstract method ``JenkinsJob._find_timer_trigger()``.
    """

    def __init__(self, trigger_based, spec):
        """Initialize a instance.

        :param bool trigger_based: if the job is trigger based or not
        :param str spec: the trigger specification

        :return nothing
        :rtype None
        """
        self._in_use = trigger_based
        self._spec = spec

    def trigger_spec(self):
        """Get the timer trigger specification, as a crontab string.

        :return: the crontab string, or None
        :rtype: str
        """
        return self._spec

    def is_defined(self):
        """Get if the job is timer trigger based or not.

        :return: True or False
        :rtype: bool
        """
        return self._in_use


class JenkinsJob(ABC):
    """Base class for all expected Jenkins job types."""

    timer_trigger_node = 'hudson.triggers.TimerTrigger'
    default_miss_desc = '*** MISSING DESCRIPTION ***'

    def __init__(self, name, config):
        """Initialize the instance.

        :param str name: the name of the job
        :param dict config: the job configuration

        :return: nothing
        :rtype: None
        """
        self.name = name
        self.description = self._find_desc(config)
        result = self._find_timer_trigger(config)

        try:
            self.timer_trigger_based = result.is_defined()
            self.timer_trigger_spec = result.trigger_spec()
        except Exception as e:
            raise InvalidFindTimerTriggerError(str(e))

    @abstractmethod
    def _find_desc(self, config):
        """Find the job description.

        :param dict config: the job configuration

        :return: the job description
        :rtype: str
        """
        pass  # pragma: no cover

    @abstractmethod
    def _find_timer_trigger(self, config):
        """Search for a timer trigger and set the instance.

        :param dict config: the job configuration

        :return: an instance of TimerTriggerResult
        :rtype: TimerTriggerResult
        """
        pass  # pragma: no cover

    def one_line_desc(self):
        """Generate a single line string from the job description.

        No parameter is required or expected.

        :return: the one line description
        :rtype: str
        """
        description = self.description
        description = description.replace('\r\n', '\n')
        lines = description.lstrip().rstrip().split('\n')
        new_lines = deque()

        for line in lines:
            if line == '':
                continue

            new_lines.append(line)

        result = ' '.join(new_lines)

        return result

    @staticmethod
    def _clean_spec(timer_spec):
        """Remove unwanted characters that might be part of the timer trigger
        specification.

        :param str timer_spec: the timer trigger specification

        :return: the cleaned timer trigger specification
        :rtype: str
        """
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
        """String representation of the instance.

        :return: a CSV string, using the pipe ("|") character as separator.
        :rtype: str
        """
        if self.timer_trigger_based:
            return '|'.join([
                self.name,
                self.__class__.__name__,
                self.one_line_desc(),
                str(self.timer_trigger_based),
                self.timer_trigger_spec
            ])
        else:
            return '|'.join([
                self.name,
                self.__class__.__name__,
                self.one_line_desc(),
                str(self.timer_trigger_based),
                'not applicable'
            ])


class PluginBasedJob(JenkinsJob):
    """Representation of a Jenkins job that is based on a plugin."""
    root_node = None

    @staticmethod
    def _plugin_type(config):
        """Find the plugin type XML node by iterating over the job
        configuration.

        :param: dict config: the job configuration

        :return: the name of the plugin type
        :rtype: str
        """
        # <flow-definition plugin="workflow-job@2.36">
        try:
            element = next(iter(config))
        except StopIteration:
            element = None

        return element

    @staticmethod
    def plugin(config):
        """Retrieve the plugin type name.

        :param: dict config: the job configuration

        :return: the plugin type name, without version information
        :rtype: str
        """
        plugin_type = PluginBasedJob._plugin_type(config)
        plugin = config[plugin_type]['@plugin']
        # plugin have their version include most of the times
        return plugin.split('@')[0].lower()

    def _find_desc(self, config):
        """Implement parent class abstract method."""
        description = None
        plugin_type = PluginBasedJob._plugin_type(config)
        description = config[plugin_type]['description']

        if description is None:
            description = self.default_miss_desc

        return description


class PipelineJob(PluginBasedJob):
    """A job that is based on the Pipeline plugin."""

    root_node = 'flow-definition'
    trigger_grandparent_node = 'org.jenkinsci.plugins.workflow.job.properties.\
PipelineTriggersJobProperty'

    def _find_timer_trigger(self, config):
        """Implement parent class abstract method."""
        result = None
        try:
            tmp = config[self.root_node]['properties']

            if self.trigger_grandparent_node in tmp:
                tmp = tmp[self.trigger_grandparent_node]

                if tmp and 'triggers' in tmp:
                    tmp = tmp['triggers']

                    if tmp and self.timer_trigger_node in tmp:
                        spec = self._clean_spec(
                                tmp[self.timer_trigger_node]['spec'])
                        # yes, there might be a existing node with nothing
                        # defined
                        if spec:
                            result = TimerTriggerResult(True, spec)
                        else:
                            result = TimerTriggerResult(True, None)
        except KeyError as e:
            raise MissingXMLElementError(element=str(e), job_name=self.name,
                                         context='a timer trigger')

        if result is None:
            result = TimerTriggerResult(False, None)

        return result


class MavenJob(PluginBasedJob):
    """A job that is based on the Maven plugin."""

    root_node = 'maven2-moduleset'
    trigger_parent_node = 'triggers'

    def _find_timer_trigger(self, config):
        """Implement parent class abstract method."""
        result = None

        try:
            tmp = config[self.root_node]

            if self.trigger_parent_node in tmp:
                tmp = tmp[self.trigger_parent_node]

                if tmp and self.timer_trigger_node in tmp:
                    spec = self._clean_spec(
                            tmp[self.timer_trigger_node]['spec'])
                    # yes, there might be a existing node with nothing
                    # defined
                    if spec:
                        result = TimerTriggerResult(True, spec)
                    else:
                        result = TimerTriggerResult(True, None)
        except KeyError as e:
            raise MissingXMLElementError(element=str(e), job_name=self.name,
                                         context='a timer trigger')

        if result is None:
            result = TimerTriggerResult(False, None)

        return result


class FreestyleJob(JenkinsJob):
    """A free style job."""

    root_node = 'project'

    def _find_desc(self, config):
        """Implement parent class abstract method."""
        description = None

        try:
            description = config[self.root_node]['description']
        except KeyError as e:
            raise MissingXMLElementError(element=str(e), job_name=self.name,
                                         context='the job description')

        if description is None:
            return self.default_miss_desc

        return description

    def _find_timer_trigger(self, config):
        """Implement parent class abstract method."""
        result = None

        try:
            tmp = config[self.root_node]['triggers']

            # tmp will be None if there is not trigger at all
            if tmp and self.timer_trigger_node in tmp:
                spec = self._clean_spec(
                        tmp[self.timer_trigger_node]['spec'])
                # yes, there might be a existing node with nothing defined
                if spec:
                    result = TimerTriggerResult(True, spec)
                else:
                    result = TimerTriggerResult(True, None)
        except KeyError as e:
            raise MissingXMLElementError(element=str(e), job_name=self.name,
                                         context='a timer trigger')

        if result is None:
            result = TimerTriggerResult(False, None)

        return result
