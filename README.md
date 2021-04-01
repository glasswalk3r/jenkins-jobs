# jenkins-jobs
[![TravisCI](https://img.shields.io/travis/glasswalk3r/jenkins-jobs.svg)](https://travis-ci.org/glasswalk3r/jenkins-jobs/branches)
[![Documentation Status](https://readthedocs.org/projects/jenkins-jobs/badge/?version=latest)](https://jenkins-jobs.readthedocs.io/en/latest/?badge=latest)

Listing all jobs on a Jenkins server with more information than their respective
names.

## Features

* Implements the `jenkins_jobs` CLI that allows the reporting of jobs in a
Jenkins server.
* The reports includes information of job name, job type, job description, if
the job is executed through a schedule and the schedule itself.
* Implements the `jenkins_exporter` CLI that allows the exporting of jobs
information to a file in a
[Shelve format](https://docs.python.org/3/library/shelve.html), which allows
to export this information and use it locally for development or even with
`jenkins_jobs` CLI.

## Requirements

* Python 3, with version >= 3.6.
* A Jenkins user and the related access token for authentication.
* The Jenkins server URL.

## How to use

You can install this project module straight from [PyPi](https://pypi.org):

```
pip install jenkins_jobs
```

Then just fire the `jenkins_job` CLI:

```
$ jenkins_jobs --user admin --token 116f3e55f677416a7c054faa20fbbcf0be --jenkins http://localhost:8080
freestyle-sample|FreestyleJob|Sample freestyle job|True|H H 1,15 1-11 *
Maven Sample|MavenJob|This is a sample Maven plugin based job, see https://plugins.jenkins.io/maven-plugin/|True|H H 1,15 1-11 *
pipeline-sample|PipelineJob|This is a sample pipeline job|True|H/15 * * * *
```

You should be able to just import this output as a CSV with `|` (pipe) as the
field separator. In future, different output formats might be provided.

## More information

Please refer to the module documentation (`README.rst`) for more details on this
project.
