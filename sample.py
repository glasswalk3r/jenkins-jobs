#!/usr/bin/env python3

import jenkins
from pprint import pprint
import xmltodict

token = '1124ffc2b50cf9f73f1a177254f8d57c9f'
server = jenkins.Jenkins('http://localhost:8080', username='alceu',
                         password=token)

for job in server.get_jobs():
    print(job)
    print('XML information:')
    pprint(xmltodict.parse(server.get_job_config(job['name'])))
