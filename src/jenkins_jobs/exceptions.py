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


class InvalidXMLConfigError(JenkinsJobError):
    def __init__(self, root_key):
        self.root_key = root_key
        self.message = f'Unexpected data, missing {root_key} root key in data structure'

    def __str__(self):
        return self.message


class NoSchemaSuppliedRESTError(JenkinsJobError):
    """Exception for Jenkins endpoints without a protocol schema.

    This exception was created to be raised when validation of Jenkins endpoint URL occurs with any one of the CLIs that
    are part of the module.

    Otherwise, Jenkins will cause an exception with the HTTP client that is harder to understand:

    requests.exceptions.MissingSchema: Invalid URL 'crumbIssuer/api/json': No schema supplied. Perhaps you meant
    http://crumbIssuer/api/json?
    """

    def __init__(self):
        """Configure the exception."""
        self.message = 'No protocol schema (http:// or https://) supplied for Jenkins REST endpoint'

    def __str__(self):
        """Stringfy the exception."""
        return self.message
