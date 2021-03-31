"""Console script for jenkins_jobs to export jobs configuration from a Jenkins server."""
import jenkins
import shelve
import xmltodict
import argparse
import sys

from jenkins_jobs.exceptions import NoSchemaSuppliedRESTError


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description='Exports Jenkins job information as Python shelve format')
    parser.add_argument('--user', required=True,
                        help='Jenkins user for REST interface')
    parser.add_argument('--token', required=True,
                        help='Jenkins token for REST interface')
    parser.add_argument('--jenkins', help='Jenkins http[s]://FQDN|IP:port', required=True)
    args = parser.parse_args()

    if not args.jenkins.startswith('http'):
        raise NoSchemaSuppliedRESTError

    server = jenkins.Jenkins(args.jenkins, username=args.user,
                             password=args.token)

    shelf = shelve.open('./jenkins_jobs.shelve', flag='n')
    print('Starting...')

    for job in server.get_jobs():

        try:
            raw_data = server.get_job_config(job['name'])
            data = xmltodict.parse(raw_data)
            job['definition'] = data
            job_name = job.pop('name')
            shelf[job_name] = job
        except jenkins.BadHTTPException as e:
            print('An exception ocurred while processing {0}: {1}'.format(
                job['name'], str(e)), file=sys.stderr)
            print('Trying to continue...')
            break

    print('Finished')


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
