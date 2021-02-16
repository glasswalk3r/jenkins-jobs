"""Tests for `jenkins_jobs` package."""
import inspect
import pytest

from jenkins_jobs.jobs import JenkinsJob, PluginBasedJob, PipelineJob, MavenJob, FreestyleJob


def test_jenkinsjob_class():
    assert inspect.isclass(JenkinsJob)
    methods = ('__init__', '_find_desc', '_find_timer_trigger', '_onliner', '_clean_spec', '__str__')

    for method in methods:
        assert hasattr(JenkinsJob, method)

    with pytest.raises(TypeError):
        JenkinsJob('foobar', {})
