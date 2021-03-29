"""Tests for `jenkins_jobs` package."""
import inspect
import pytest
import xmltodict

from jenkins_jobs.jobs import JenkinsJob, PluginBasedJob, PipelineJob, MavenJob, FreestyleJob
from jenkins_jobs.exceptions import MissingXMLElementError


def xml_config(xml_filename):
    config = {}

    with open(f'tests/raw_data/{xml_filename}', 'r') as fp:
        config['definition'] = xmltodict.parse(fp.read())

    return config


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

    attribs = ('root_node', 'trigger_cfg_node')

    for attribute in attribs:
        assert hasattr(PluginBasedJob, attribute)


def test_pluginbasedjob_methods():
    methods = ('_plugin_type', 'plugin')

    for method in methods:
        assert hasattr(PluginBasedJob, method)
        inspect.ismethod(getattr(PluginBasedJob, method))


def test_pluginbasedjob_instance():
    config = xml_config('workflow-job-plugin.xml')

    with pytest.raises(MissingXMLElementError) as excinfo:
        PluginBasedJob('Workflow Job Plugin sample', config)

    # fails because the class attribute root_node is None
    assert 'None' in str(excinfo.value)


def test_pipelinejob_instance():
    config = xml_config('workflow-job-plugin.xml')
    instance = PipelineJob('Workflow Job Plugin sample', config)
    assert instance.root_node == 'flow-definition'
    assert instance.description == 'Sample description for PipelineJob'
    assert instance.timer_trigger_based is False
