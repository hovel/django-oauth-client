from rest_framework.exceptions import APIException


class LockIntegrationError(APIException):
    status_code = 500
    default_detail = 'Lock Integration is unsuccess.'
    default_code = "lock_integration_error"
