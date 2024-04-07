============
Jenkins Jobs
============


.. image:: https://img.shields.io/pypi/v/jenkins_jobs.svg
        :target: https://pypi.python.org/pypi/jenkins_jobs

.. image:: https://github.com/glasswalk3r/jenkins-jobs/actions/workflows/main.yml/badge.svg
        :target: https://github.com/glasswalk3r/jenkins-jobs/actions/workflows/main.yml

Listing all jobs on a Jenkins server with more information than just their
respective names.


* Free software: GNU General Public License v3


Features
--------

* Implements the ``jenkins_jobs`` CLI that allows the reporting of jobs in a
  Jenkins server.
* The reports includes information of job name, job type, job description, if
  the job is executed through a schedule and the schedule itself.
* Implements the ``jenkins_exporter`` CLI that allows the exporting of jobs
  information to a file in a `Shelve format <https://docs.python.org/3/library/shelve.html>`_,
  which allows to export this information and use it locally for development or
  even with ``jenkins_jobs`` CLI.

Rationale
---------

Some time ago I got to migrate jobs from three Jenkins servers with about 800
jobs included among them and the need to migrate those jobs to somewhere else.

I will not discuss the reasons for such humongous amount, but anyway I would
need to understand what those jobs were, how they were built and other details,
so I could come up with a better strategy of migration.

For my surprise, no tooling was available to use at that time.

Listing with Jenkins CLI
========================

My first attempt was to use the official Jenkins CLI to extract that
information.

If you are curious, you can use `Vagrant <https://www.vagrantup.com>`_ with
the following ``Vagrantfile`` and download the Vagrant VirtualBox box I
created with a sample Jenkins server and some examples jobs over there:

::

  Vagrant.configure("2") do |config|
    config.vm.box = "arfreitas/jenkins-centos7"
    config.vm.box_version = "0.0.1"
    config.vm.network 'forwarded_port', guest: 8080, host: 8080, id: 'jenkins'

    config.vm.provider 'virtualbox' do |vb|
      vb.gui = false
      vb.memory = '2048'
      vb.cpus = '2'
      vb.name = 'jenkins-sample'
  end

These are the credentials already setup:

* user: admin
* password: admin
* token: 116f3e55f677416a7c054faa20fbbcf0be

Finally, fire up the VM:

::

  $ vagrant up


After the setup is complete, fire up the commands below:

::

  $ vagrant ssh
  $ java -jar jenkins-cli.jar -s http://localhost:8080/ -webSocket -auth admin:116f3e55f677416a7c054faa20fbbcf0be list-jobs
  freestyle-sample
  pipeline-sample


Not a very exciting output. You will get the job names and that's it.

Listing with the REST API
=========================

So then I tried the Jenkins
`REST API <https://python-jenkins.readthedocs.io/en/latest/>`_ with the ``sample.py`` Python 3 program:

::

  $ cd /vagrant
  $ ./sample.py
  {'_class': 'hudson.model.FreeStyleProject', 'name': 'freestyle-sample', 'url': 'http://localhost:8080/job/freestyle-sample/', 'color': 'notbuilt', 'fullname': 'freestyle-sample'}
  XML information:
  OrderedDict([('project',
                OrderedDict([('keepDependencies', 'false'),
                             ('properties', None),
                             ('scm',
                              OrderedDict([('@class', 'hudson.scm.NullSCM')])),
                             ('canRoam', 'false'),
                             ('disabled', 'false'),
                             ('blockBuildWhenDownstreamBuilding', 'false'),
                             ('blockBuildWhenUpstreamBuilding', 'false'),
                             ('triggers', None),
                             ('concurrentBuild', 'false'),
                             ('builders', None),
                             ('publishers', None),
                             ('buildWrappers', None)]))])
  {'_class': 'org.jenkinsci.plugins.workflow.job.WorkflowJob', 'name': 'pipeline-sample', 'url': 'http://localhost:8080/job/pipeline-sample/', 'color': 'notbuilt', 'fullname': 'pipeline-sample'}
  XML information:
  OrderedDict([('flow-definition',
                OrderedDict([('@plugin', 'workflow-job@2.40'),
                             ('keepDependencies', 'false'),
                             ('properties', None),
                             ('triggers', None),
                             ('disabled', 'false')]))])



If you take in consideration this is almost raw output, it's an improvement
because of the additional details, but far from enough.

First because part of the output is XML. Second, it is not exactly easy to
understand the output.

Worst, the XML specification depends on the job underline mechanism: if the
job is based on a plugin, the XML format will depend on that plugin, not on
Jenkins.

Getting documentation about the XML format is another challenge.

Solution
========

What the jenkins-jobs project tries to do is to map desired information from
the XML format based on the Python classes under ``jenkins_jobs.jobs`` module.

References
----------

* The `JenkinsAPI <https://jenkinsapi.readthedocs.io/en/latest/using_jenkinsapi.html>`_ project.
* The `python-jenkins <https://python-jenkins.readthedocs.io/en/latest/index.html>`_ project.
* Stackoverflow question: `Groovy to list all jobs <https://support.cloudbees.com/hc/en-us/articles/226941767-Groovy-to-list-all-jobs>`_.
* Stackoverflow question: `Determining the type of Jenkins project <https://stackoverflow.com/questions/45064038/determining-the-type-of-jenkins-project>`_.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
