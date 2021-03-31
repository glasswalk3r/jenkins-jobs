"""Tests for `jenkins_jobs` package."""
import inspect
import pytest

from jenkins_jobs.retrievers import Retriever, FileSystemRetriever, RESTRetriever
from jenkins_jobs.exceptions import UnknownJobTypeError, InvalidXMLConfigError


def test_retriever_class():
    assert inspect.isclass(Retriever)
    assert hasattr(Retriever, 'plugin_based_jobs')
    assert Retriever.plugin_based_jobs.__class__.__name__ == 'dict'


def test_retriever_methods():
    methods = ('all_jobs', '_job_builder')

    for method in methods:
        assert hasattr(Retriever, method)
        inspect.ismethod(getattr(Retriever, method))


@pytest.mark.parametrize('job_name, xml_filename, klass', [
    ('freestyle sample', 'freestyle-job-trigger.xml', 'FreestyleJob'),
    ('workflow sample', 'workflow-job-plugin-timer.xml', 'PipelineJob'),
    ('maven sample', 'maven-job-plugin.xml', 'MavenJob')
])
def test_retriever_builder(job_name, xml_filename, klass, helpers):
    config = helpers.xml_config(xml_filename)
    instance = Retriever._job_builder(job_name, config)
    assert instance.__class__.__name__ == klass


@pytest.mark.parametrize('klass', [FileSystemRetriever, RESTRetriever])
def test_retriever_subclass(klass):
    assert issubclass(klass, Retriever)
    assert hasattr(klass, '__init__')


def test_retriever_bogus_raises_exception(helpers):
    config = helpers.xml_config('bogus-plugin.xml')

    with pytest.raises(UnknownJobTypeError) as excinfo:
        Retriever._job_builder('Bogus Plugin sample', config)

    assert 'foobar' in str(excinfo.value)


def test_retriever_invalid_raises_exception():
    with pytest.raises(InvalidXMLConfigError) as excinfo:
        Retriever._job_builder('Empty Plugin sample', {})

    assert 'None' in str(excinfo.value)
