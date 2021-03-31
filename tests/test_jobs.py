"""Tests for `jenkins_jobs` package."""
import inspect
import pytest

from jenkins_jobs.jobs import JenkinsJob, PluginBasedJob, PipelineJob, MavenJob, FreestyleJob
from jenkins_jobs.exceptions import MissingXMLElementError


def test_jenkinsjob_class():
    assert inspect.isclass(JenkinsJob)

    with pytest.raises(TypeError) as excinfo:
        JenkinsJob('foobar', {})

    assert "Can't instantiate abstract class JenkinsJob with abstract methods _find_desc, _find_timer_trigger" in str(
        excinfo.value)


def test_jenkinsjob_methods():
    methods = ('__init__', '_find_desc', '_find_timer_trigger', '_onliner', '_clean_spec', '__str__')

    for method in methods:
        assert hasattr(JenkinsJob, method)
        inspect.ismethod(getattr(JenkinsJob, method))


def test_clean_spec_crlf_multiple():
    data = 'This is a\r\nsample description\r\nwith CRLF new lines.'
    expected = 'This is a\nsample description\nwith CRLF new lines.'

    assert expected == JenkinsJob._clean_spec(data)


def test_clean_spec_crlf_comment():
    data = '#This is a comment\r\nFollowed by an actually comment'
    expected = 'Followed by an actually comment'

    assert expected == JenkinsJob._clean_spec(data)


def test_clean_spec_lf_comment():
    data = '#This is a comment\nFollowed by an actually comment'
    expected = 'Followed by an actually comment'

    assert expected == JenkinsJob._clean_spec(data)


def test_clean_spec_empty_line():
    data = '\r\nFollowed by an actually comment'
    expected = 'Followed by an actually comment'

    assert expected == JenkinsJob._clean_spec(data)


def test_pluginbasedjob_class():
    assert issubclass(PluginBasedJob, JenkinsJob)

    attribs = tuple(['root_node'])

    for attribute in attribs:
        assert hasattr(PluginBasedJob, attribute)


def test_pluginbasedjob_methods():
    methods = ('_plugin_type', 'plugin')

    for method in methods:
        assert hasattr(PluginBasedJob, method)
        inspect.ismethod(getattr(PluginBasedJob, method))


def test_pluginbasedjob_instance_raises_exception(helpers):
    config = helpers.xml_config('workflow-job-plugin.xml')
    assert PluginBasedJob.plugin(config) == 'workflow-job'

    with pytest.raises(TypeError) as excinfo:
        PluginBasedJob('Workflow Job Plugin sample', config)

    assert str(excinfo.value).startswith("Can't instantiate abstract class PluginBasedJob")
    assert '_find_timer_trigger' in str(excinfo.value)


def test_pipelinejob_class():
    assert issubclass(PipelineJob, PluginBasedJob)
    assert hasattr(PipelineJob, 'trigger_grandparent_node')


def test_pipelinejob_instance(helpers):
    config = helpers.xml_config('workflow-job-plugin.xml')
    assert PipelineJob.plugin(config) == 'workflow-job'
    instance = PipelineJob('Workflow Job Plugin sample', config)
    assert instance.root_node == 'flow-definition'
    assert instance.description == 'Sample description for PipelineJob'
    assert instance.timer_trigger_based is False


def test_pipelinejob_instance_scheduler(helpers):
    config = helpers.xml_config('workflow-job-plugin-timer.xml')
    instance = PipelineJob('Workflow Job Plugin sample', config)
    assert instance.root_node == 'flow-definition'
    assert instance.description == 'This is a sample pipeline job with timer trigger'
    assert instance.timer_trigger_based is True
    assert instance.timer_trigger_spec == 'H/15 * * * *'


def test_mavenjob_class():
    assert issubclass(MavenJob, PluginBasedJob)
    assert hasattr(MavenJob, 'trigger_parent_node')


def test_mavenjob_instance(helpers):
    config = helpers.xml_config('maven-job-plugin.xml')
    instance = MavenJob('Maven Job Plugin sample', config)
    assert instance.root_node == 'maven2-moduleset'
    assert instance.description == 'This is a sample Maven plugin based job, see \
https://plugins.jenkins.io/maven-plugin/'
    assert instance.timer_trigger_based is True
    assert instance.timer_trigger_spec == 'H H 1,15 1-11 *'


def test_freestyle_class():
    assert issubclass(FreestyleJob, JenkinsJob)
    assert hasattr(FreestyleJob, 'root_node')


@pytest.mark.parametrize('job_name, xml_filename, element, context, klass', [
    ('maven job', 'maven-job-plugin-bogus.xml', 'spec', 'a timer trigger', MavenJob),
    ('freestyle job', 'freestyle-job-bogus.xml', 'description', 'the job description', FreestyleJob),
    ('pipeline job', 'workflow-job-plugin-bogus.xml', 'spec', 'a timer trigger', PipelineJob)
])
def test_bogus_instance(job_name, xml_filename, element, context, klass, helpers):
    config = helpers.xml_config(xml_filename)

    with pytest.raises(MissingXMLElementError) as excinfo:
        klass(job_name, config)

    expected = f'Could not locate \'{element}\' element while searching for {context} in "{job_name}"'
    assert str(excinfo.value) == expected


def test_freestyle_instance(helpers):
    config = helpers.xml_config('freestyle-job.xml')
    instance = FreestyleJob('freestyle-sample', config)
    assert instance.root_node == 'project'
    assert instance.description == 'Sample freestyle job'
    assert instance.timer_trigger_based is False
    assert str(instance) == 'freestyle-sample|FreestyleJob|Sample freestyle job|False|not applicable'


def test_freestyle_instance_trigger(helpers):
    config = helpers.xml_config('freestyle-job-trigger.xml')
    instance = FreestyleJob('freestyle-sample', config)
    assert instance.root_node == 'project'
    assert instance.description == 'Sample freestyle job'
    assert instance.timer_trigger_based is True
    assert str(instance) == 'freestyle-sample|FreestyleJob|Sample freestyle job|True|H H 1,15 1-11 *'


def test_freestyle_instance_no_desc(helpers):
    config = helpers.xml_config('freestyle-job-nodesc.xml')
    instance = FreestyleJob('freestyle-sample', config)
    assert instance.root_node == 'project'
    assert instance.description == '*** MISSING DESCRIPTION ***'
    assert instance.timer_trigger_based is False
    assert str(instance) == 'freestyle-sample|FreestyleJob|*** MISSING DESCRIPTION ***|False|not applicable'
