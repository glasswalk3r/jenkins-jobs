# Listing Jenkins Jobs

## Listing with Jenkins CLI

```
[vagrant@localhost ~]$ java -jar jenkins-cli.jar -s http://localhost:8080/ -webSocket -auth alceu:11890772629890c1dfaf24cb6aa7635e94 list-jobs
freestyle
pipeline
```

## Refences

https://jenkinsapi.readthedocs.io/en/latest/using_jenkinsapi.html
https://python-jenkins.readthedocs.io/en/latest/index.html
https://support.cloudbees.com/hc/en-us/articles/226941767-Groovy-to-list-all-jobs
https://stackoverflow.com/questions/45064038/determining-the-type-of-jenkins-project

