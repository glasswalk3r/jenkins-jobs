# jenkins-jobs

Listing all jobs on a Jenkins server with more information than their respective
names.

## Rationale

Some months ago I got three Jenkins servers with ~800 jobs included among them
and the need to migrate those jobs to somewhere else.

I will not discuss the reasons for such humongous amount, but anyway I would
need to understand what those jobs were, how they were built and other details,
so I could come up with a better strategy of migration.

For my surprise, nothing was available to use at that time.

## Listing with Jenkins CLI

First attempt was to use the official Jenkins CLI to extract that information.
If you are curious, I included a `Vagrantfile` to start your own Jenkins server
with zero configuration:

```
$ vagrant up
```

After the setup is complete, fire up the commands below:

```
$ vagrant ssh
$ java -jar jenkins-cli.jar -s http://localhost:8080/ -webSocket -auth admin:116f3e55f677416a7c054faa20fbbcf0be list-jobs
freestyle-sample
pipeline-sample
```

Not very exciting output.

So I tried the Jenkins
[REST API](https://python-jenkins.readthedocs.io/en/latest/) with the
`sample.py` Python 3 program:

```
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
```

If you take in consideration this is almost raw output, it's an improvement
because of the additional details, but far to be enough.

## Refences

* The [JenkinsAPI](https://jenkinsapi.readthedocs.io/en/latest/using_jenkinsapi.html) project.
* The [python-jenkins](https://python-jenkins.readthedocs.io/en/latest/index.html) project.
* Stackoverflow question: [Groovy to list all jobs](https://support.cloudbees.com/hc/en-us/articles/226941767-Groovy-to-list-all-jobs).
* Stackoverflow question: [Determining the type of Jenkins project](https://stackoverflow.com/questions/45064038/determining-the-type-of-jenkins-project).
