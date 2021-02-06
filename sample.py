#!/usr/bin/python3

import jenkins
from pprint import pprint
import xmltodict

token = '11890772629890c1dfaf24cb6aa7635e94'
server = jenkins.Jenkins('http://localhost:8080', username='alceu',
                         password=token)

for job in server.get_jobs():
    pprint(xmltodict.parse(server.get_job_config(job['name'])))
