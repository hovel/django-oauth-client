from django.core.exceptions import Exception


class LockIntegrationError(Exception):
    status_code = 500
    default_detail = 'Lock Integration is unsuccess.'
    default_code = "lock_integration_error"
