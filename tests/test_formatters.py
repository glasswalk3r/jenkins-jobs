"""Tests for `jenkins_jobs.formatters`."""

import inspect
import json

import pytest

from jenkins_jobs.formatters import (
    ReportFormatter,
    CSVFormatter,
    HTMLFormatter,
    FORMATTERS,
    get_formatter,
)
from jenkins_jobs.jobs import FreestyleJob


@pytest.fixture
def jobs(helpers):
    freestyle = FreestyleJob(
        'freestyle-sample', helpers.xml_config('freestyle-job.xml'))
    triggered = FreestyleJob(
        'freestyle-triggered', helpers.xml_config('freestyle-job-trigger.xml'))

    return [freestyle, triggered]


def test_reportformatter_class():
    assert inspect.isclass(ReportFormatter)

    with pytest.raises(TypeError) as excinfo:
        ReportFormatter()

    assert 'abstract method' in str(excinfo.value)


def test_formatters_registry():
    assert FORMATTERS['csv'] is CSVFormatter
    assert FORMATTERS['html'] is HTMLFormatter


def test_get_formatter():
    assert isinstance(get_formatter('csv'), CSVFormatter)
    assert isinstance(get_formatter('html'), HTMLFormatter)

    with pytest.raises(KeyError):
        get_formatter('bogus')


def test_csvformatter_generate(jobs):
    formatter = CSVFormatter()
    result = formatter.generate(jobs)
    lines = result.split('\n')

    assert len(lines) == len(jobs)

    for job, line in zip(jobs, lines):
        assert line == str(job)


def test_csvformatter_generate_empty():
    formatter = CSVFormatter()
    assert formatter.generate([]) == ''


def test_htmlformatter_generate(jobs):
    formatter = HTMLFormatter()
    result = formatter.generate(jobs)

    assert result.startswith('<!DOCTYPE html>')
    assert '<script src="{0}"></script>'.format(
        HTMLFormatter.chartjs_url) in result
    assert 'new Chart(' in result
    assert '2 job(s) found.' in result

    for job in jobs:
        assert job.name in result
        assert job.__class__.__name__ in result

    assert json.dumps(['FreestyleJob']) in result
    assert json.dumps([2]) in result


def test_htmlformatter_generate_empty():
    formatter = HTMLFormatter()
    result = formatter.generate([])

    assert '0 job(s) found.' in result
    assert json.dumps([]) in result


def test_htmlformatter_escapes_html(helpers):
    config = helpers.xml_config('freestyle-job.xml')
    job = FreestyleJob('<script>alert(1)</script>', config)

    formatter = HTMLFormatter()
    result = formatter.generate([job])

    assert '<script>alert(1)</script>' not in result
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in result


def test_htmlformatter_missing_description(helpers):
    config = helpers.xml_config('freestyle-job-nodesc.xml')
    job = FreestyleJob('freestyle-sample', config)

    formatter = HTMLFormatter()
    result = formatter.generate([job])

    assert '<span class="missing-desc">MISSING DESCRIPTION</span>' in result
    assert '*' not in result.split('<tbody>')[1].split('</tbody>')[0]
