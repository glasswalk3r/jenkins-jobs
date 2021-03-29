class JenkinsJobError(Exception):
    pass


class MissingXMLElementError(JenkinsJobError):
    def __init__(self, element, context, job_name):
        self.message = 'Could not locate {0} element while searching for {1} in "{2}"'.format(
            element, context, job_name)

    def __str__(self):
        return self.message


class UnknownJobTypeError(JenkinsJobError):
    def __init__(self, job_type):
        self.job_type = job_type
        self.message = f'Unknown job type "{self.job_type}"'

    def __str__(self):
        return self.message
