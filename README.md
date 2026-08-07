# jenkins-jobs

[![Python application](https://github.com/glasswalk3r/jenkins-jobs/actions/workflows/main.yml/badge.svg)](https://github.com/glasswalk3r/jenkins-jobs/actions/workflows/main.yml)

A CLI programa that lists all jobs on a Jenkins server with more information
than their respective names.

## Features

* Implements the `jenkins_jobs` CLI that allows the reporting of jobs in a
Jenkins server. The reports includes information of job name, job type, job description, if
the job is executed through a schedule and the schedule itself.
* Implements the `jenkins_exporter` CLI that allows the exporting of jobs
information to a file in a
[Shelve format](https://docs.python.org/3/library/shelve.html), which allows
to export this information and use it locally for development or even with
`jenkins_jobs` CLI.

## Requirements

* Python 3, with version >= 3.8.
* A Jenkins user and the related access token for authentication.
* The Jenkins server URL.

## How to use

You can install this project module straight from [PyPi](https://pypi.org):

```
pip install jenkins_jobs
```

Then just fire the `jenkins_jobs` CLI:

```
$ jenkins_jobs --user admin --token 116f3e55f677416a7c054faa20fbbcf0be --jenkins http://localhost:8080
freestyle-sample|FreestyleJob|Sample freestyle job|True|H H 1,15 1-11 *
Maven Sample|MavenJob|This is a sample Maven plugin based job, see https://plugins.jenkins.io/maven-plugin/|True|H H 1,15 1-11 *
pipeline-sample|PipelineJob|This is a sample pipeline job|True|H/15 * * * *
```

By default, the output is a CSV with `|` (pipe) as the field separator, printed
to stdout, so you should be able to just import it. Pass `--format html`
instead to generate a self-contained HTML5 report with a table of all jobs
and a bar chart (built with [Chart.js](https://www.chartjs.org/)) of the
total number of jobs by type; it is written to `report.html` in the current
directory rather than printed:

```
$ jenkins_jobs --user admin --token 116f3e55f677416a7c054faa20fbbcf0be --jenkins http://localhost:8080 --format html
HTML report written to report.html
```

`--format` accepts `csv` (the default) or `html`; anything else is rejected.

### Exporting jobs for local/offline use

The `jenkins_exporter` CLI connects to a Jenkins server and dumps every job's
configuration into a local
[Shelve](https://docs.python.org/3/library/shelve.html) file
(`./jenkins_jobs.shelve` in the current directory), so it can be replayed
later without hitting the server again:

```
$ jenkins_exporter --user admin --token 116f3e55f677416a7c054faa20fbbcf0be --jenkins http://localhost:8080
Starting...
Finished
```

Pass that file to `jenkins_jobs` with `--shelve-file` and it will read from it
instead of connecting to Jenkins over the REST API. `--shelve-file` cannot be
combined with `--user`/`--token`/`--jenkins` — it's one or the other:

```
$ jenkins_jobs --shelve-file ./jenkins_jobs.shelve
```

## More information

Please visit [readthedocs.io](https://jenkins-jobs.readthedocs.io/en/latest/)
for more details on this project.
