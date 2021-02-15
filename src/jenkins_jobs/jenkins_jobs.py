"""Main module."""

from collections import deque
from abc import ABC, abstractmethod
import sys


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
        pass

    @abstractmethod
    def _find_timer_trigger(self, config):
        pass

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

    def _clean_spec(self, timer_spec):
        spec = None

        if timer_spec is None:
            return spec

        normalized = timer_spec.replace('\r\n', '\n')
        lines = normalized.split('\n')

        for line in lines:
            if line.startswith('#') or line == '':
                continue
            else:
                spec = line

        return spec

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
    trigger_cfg_node = 'org.jenkinsci.plugins.workflow.job.properties.Pipeline\
TriggersJobProperty'

    @staticmethod
    def _plugin_type(config):
        return next(iter(config['definition']))

    @staticmethod
    def plugin(config):
        plugin_type = PluginBasedJob._plugin_type(config)
        plugin = config['definition'][plugin_type]['@plugin']
        # plugin have their version include must of the times
        return plugin.split('@')[0].lower()

    def _find_desc(self, config):
        plugin_type = PluginBasedJob._plugin_type(config)
        return config['definition'][plugin_type]['description']

    def _find_timer_trigger(self, config):
        try:
            tmp = config['definition'][self.root_node]['properties']

            if self.trigger_cfg_node in tmp:
                tmp = tmp[self.trigger_cfg_node]

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
            msg = 'Could not locate "{0}" key while searching for a timer \
trigger in {1}'
            raise Exception(msg.format(e, self.name))


class PipelineJob(PluginBasedJob):
    root_node = 'flow-definition'


class MavenJob(PluginBasedJob):
    root_node = 'maven2-moduleset'


class FreestyleJob(JenkinsJob):
    root_node = 'project'

    def _find_desc(self, config):
        try:
            return config['definition'][self.root_node]['description']
        except KeyError as e:
            print('Missing {} property'.format(e), file=sys.stderr)

        return None

    def _find_timer_trigger(self, config):
        try:
            tmp = config['definition'][self.root_node]['triggers']

            # tmp will be None if there is not trigger at all
            if tmp and self.timer_trigger_node in tmp:
                self.timer_trigger_spec = self._clean_spec(
                    tmp[self.timer_trigger_node]['spec'])
                # yes, there might be a existing node with nothing defined
                if self.timer_trigger_spec:
                    self.timer_trigger_based = True
        except KeyError as e:
            msg = 'Could not locate {} while searching for a time trigger'
            raise Exception(msg.format(e))
