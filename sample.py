#!/usr/bin/env python3

import jenkins
from pprint import pprint
import xmltodict

token = '117037154ffabf2db2fc72a7bc8d33d116'
server = jenkins.Jenkins('http://localhost:8080', username='admin',
                         password=token)

for job in server.get_jobs():
    print(job)
    print('XML information:')
    pprint(xmltodict.parse(server.get_job_config(job['name'])))
