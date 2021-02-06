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

After the setup is complete, fire up the commands below. Be sure to replace
`you:yourkey` with your proper credentials after creating an user in Jenkins:

```
$ vagrant ssh
$ java -jar jenkins-cli.jar -s http://localhost:8080/ -webSocket -auth you:yourkey list-jobs
freestyle
pipeline
```

Not very exciting output. So I tried the REST API with the `sample.py` Python 3
program. Same thing, basically.

## Refences

* The [JenkinsAPI](https://jenkinsapi.readthedocs.io/en/latest/using_jenkinsapi.html) project.
* The [python-jenkins](https://python-jenkins.readthedocs.io/en/latest/index.html) project.
* Stackoverflow question: [Groovy to list all jobs](https://support.cloudbees.com/hc/en-us/articles/226941767-Groovy-to-list-all-jobs).
* Stackoverflow question: [Determining the type of Jenkins project](https://stackoverflow.com/questions/45064038/determining-the-type-of-jenkins-project).
