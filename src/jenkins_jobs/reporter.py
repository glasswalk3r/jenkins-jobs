"""Console script for jenkins_jobs to report jobs at a Jenkins server."""
import argparse
import sys
import os

from jenkins_jobs.retrievers import RESTRetriever, FileSystemRetriever
from jenkins_jobs.exceptions import NoSchemaSuppliedRESTError


def main():  # pragma: no cover
    """Console script for jenkins_jobs."""
    parser = argparse.ArgumentParser(
        description='Extracts Jenkins job information and generates a report')
    parser.add_argument('--user', required=True,
                        help='Jenkins user for REST interface')
    parser.add_argument('--token', required=True,
                        help='Jenkins token for REST interface')
    parser.add_argument('--jenkins', help='Jenkins http[s]://FQDN|IP:port', required=True)

    if 'JOBS_REPORTER_DATA' in os.environ:
        jobs_retriever = FileSystemRetriever(os.environ['JOBS_REPORTER_DATA'])
    else:
        args = parser.parse_args()

        if not args.jenkins.startswith('http'):
            raise NoSchemaSuppliedRESTError

        jobs_retriever = RESTRetriever(user=args.user, token=args.token,
                                       jenkins_server=args.jenkins)

    jobs = jobs_retriever.all_jobs()

    for job in jobs():
        print(job)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
