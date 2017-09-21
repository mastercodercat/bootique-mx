from rest_framework import exceptions


class APIException(exceptions.APIException):
    def __init__(self, *args, **kwargs):
        if 'status' in kwargs:
            self.status = kwargs.pop('status')
        else:
            self.status = 200
        super(APIException, self).__init__(*args, **kwargs)
