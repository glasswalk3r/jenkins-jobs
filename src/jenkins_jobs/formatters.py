"""Report formatters that turn a collection of jobs into report content."""

import json
from abc import ABC, abstractmethod
from collections import Counter
from html import escape
from string import Template

from jenkins_jobs.jobs import JenkinsJob


class ReportFormatter(ABC):
    """Base class for all report formatters.

    A formatter turns an iterable of ``JenkinsJob`` instances into the final
    report content, as a single string that can be printed or written to a
    file.
    """

    @abstractmethod
    def generate(self, jobs):
        """Generate the report content.

        :param jobs: an iterable of ``JenkinsJob`` instances

        :return: the report content
        :rtype: str
        """
        pass  # pragma: no cover


class CSVFormatter(ReportFormatter):
    """Generate a pipe ("|") separated report, one line per job.

    This is what ``str(job)`` already produces for a single job; this
    formatter joins one such line per job with a newline, keeping the
    historical output format of this project.
    """

    def generate(self, jobs):
        """Implement parent class abstract method."""
        return '\n'.join(str(job) for job in jobs)


class HTMLFormatter(ReportFormatter):
    """Generate a self-contained HTML5 report.

    Besides a table listing every job, the report includes a vertical bar
    chart, rendered client-side with `Chart.js <https://www.chartjs.org/>`_
    (loaded from a public CDN, since this package doesn't otherwise ship or
    manage any JavaScript assets), showing the total number of jobs grouped
    by job type.
    """

    chartjs_url = \
        'https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js'

    _page_template = Template('''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Jenkins Jobs Report</title>
<script src="$chartjs_url"></script>
<style>
  body { font-family: Arial, Helvetica, sans-serif; margin: 2rem; color: #1b1b1b; }
  h1 { margin-bottom: 0.25rem; }
  .summary { color: #555; margin-bottom: 2rem; }
  #chart-container { max-width: 700px; margin: 0 auto 2.5rem; }
  .table-wrapper { width: 100%; overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; table-layout: fixed; }
  th, td {
    border: 1px solid #ddd;
    padding: 0.5rem 0.75rem;
    text-align: left;
    vertical-align: top;
    overflow-wrap: break-word;
    word-break: break-word;
  }
  th { background-color: #2d2d2d; color: #fff; position: sticky; top: 0; }
  tr:nth-child(even) { background-color: #f7f7f7; }
  th:nth-child(1), td:nth-child(1) { width: 18%; }
  th:nth-child(2), td:nth-child(2) { width: 12%; }
  th:nth-child(3), td:nth-child(3) { width: 40%; }
  th:nth-child(4), td:nth-child(4) { width: 12%; }
  th:nth-child(5), td:nth-child(5) { width: 18%; }
  .missing-desc { color: #c0392b; font-weight: bold; }
</style>
</head>
<body>
<h1>Jenkins Jobs Report</h1>
<p class="summary">$total job(s) found.</p>
<div id="chart-container">
  <canvas id="jobTypesChart"></canvas>
</div>
<div class="table-wrapper">
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Description</th>
        <th>Timer triggered</th>
        <th>Timer spec</th>
      </tr>
    </thead>
    <tbody>
$rows
    </tbody>
  </table>
</div>
<script>
  new Chart(document.getElementById('jobTypesChart'), {
    type: 'bar',
    data: {
      labels: $labels,
      datasets: [{
        label: 'Jobs by type',
        data: $data,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: 'x',
      scales: {
        y: {
          beginAtZero: true,
          ticks: { precision: 0 }
        }
      },
      plugins: {
        legend: { display: false },
        title: { display: true, text: 'Jobs by type' }
      }
    }
  });
</script>
</body>
</html>
''')

    def generate(self, jobs):
        """Implement parent class abstract method."""
        jobs = list(jobs)
        counts = Counter(job.__class__.__name__ for job in jobs)
        labels = sorted(counts)
        data = [counts[label] for label in labels]
        rows = '\n'.join(self._row(job) for job in jobs)

        return self._page_template.substitute(
            chartjs_url=self.chartjs_url,
            total=len(jobs),
            rows=rows,
            labels=json.dumps(labels),
            data=json.dumps(data),
        )

    @staticmethod
    def _row(job):
        """Render a single job as a HTML table row.

        :param JenkinsJob job: the job to render

        :return: the ``<tr>`` markup for the job
        :rtype: str
        """
        if job.timer_trigger_based:
            spec = job.timer_trigger_spec or ''
        else:
            spec = 'not applicable'

        return '''    <tr>
      <td>{name}</td>
      <td>{job_type}</td>
      <td>{description}</td>
      <td>{triggered}</td>
      <td>{spec}</td>
    </tr>'''.format(
            name=escape(job.name),
            job_type=escape(job.__class__.__name__),
            description=HTMLFormatter._description_html(job),
            triggered=job.timer_trigger_based,
            spec=escape(spec),
        )

    @staticmethod
    def _description_html(job):
        """Render a job's description as HTML.

        The CSV-friendly ``*** MISSING DESCRIPTION ***`` marker doesn't read
        well as HTML, so it's rendered as bold, red text instead, without the
        asterisks.

        :param JenkinsJob job: the job to render the description of

        :return: the HTML markup for the description cell
        :rtype: str
        """
        description = job.one_line_desc()

        if description == JenkinsJob.default_miss_desc:
            label = escape(JenkinsJob.default_miss_desc.strip('* '))
            return f'<span class="missing-desc">{label}</span>'

        return escape(description)


#: Formatters keyed by the ``--format`` CLI option value.
FORMATTERS = {
    'csv': CSVFormatter,
    'html': HTMLFormatter,
}


def get_formatter(name):
    """Retrieve a formatter instance by name.

    :param str name: one of the keys in ``FORMATTERS`` (``csv`` or ``html``)

    :return: a formatter instance
    :rtype: ReportFormatter
    :raises KeyError: if ``name`` isn't a known formatter
    """
    return FORMATTERS[name]()
