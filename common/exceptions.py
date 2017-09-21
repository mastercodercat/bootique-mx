from rest_framework import exceptions


class APIException(exceptions.APIException):
    def __init__(self, *args, **kwargs):
        if 'status' in kwargs:
            self.status = kwargs.pop('status')
        else:
            self.status = 500

        if 'response' in kwargs:
            self.response = kwargs.pop('response')
        else:
            self.response = None

        super(APIException, self).__init__(*args, **kwargs)
