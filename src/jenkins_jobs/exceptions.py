class JenkinsJobException(Exception):
    pass


class MissingXMLElementError(JenkinsJobException):
    def __init__(self, element, context, job_name):
        self.message = 'Could not locate "{0}" element while searching for {1} in "{2}"'.format(
            element, context, job_name)

    def __str__(self):
        return self.message
