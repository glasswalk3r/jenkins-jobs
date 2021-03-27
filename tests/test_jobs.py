"""Tests for `jenkins_jobs` package."""
import inspect
import pytest

from jenkins_jobs.jobs import JenkinsJob, PluginBasedJob, PipelineJob, MavenJob, FreestyleJob


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
