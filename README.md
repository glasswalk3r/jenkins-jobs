# Listing Jenkins Jobs

## Listing with Jenkins CLI

```
[vagrant@localhost ~]$ java -jar jenkins-cli.jar -s http://localhost:8080/ -webSocket -auth alceu:11890772629890c1dfaf24cb6aa7635e94 list-jobs
freestyle
pipeline
```

## Refences

* The [JenkinsAPI](https://jenkinsapi.readthedocs.io/en/latest/using_jenkinsapi.html) project.
* The [python-jenkins](https://python-jenkins.readthedocs.io/en/latest/index.html) project.
* Stackoverflow question: [Groovy to list all jobs](https://support.cloudbees.com/hc/en-us/articles/226941767-Groovy-to-list-all-jobs).
* Stackoverflow question: [Determining the type of Jenkins project](https://stackoverflow.com/questions/45064038/determining-the-type-of-jenkins-project).

