import typing as t
from werkzeug.exceptions import UnprocessableEntity, Conflict, Gone
from .commontypes import FormField

"""Custom exceptions that the API can raise are defined here. API's response in case of
exceptional cases is to return a non 200 error code and a JSON body that will have a 
readable snake case error keyword. The JSON in case of exception is:
{
    "error": {
        "code": "",
        "description": ""
    }
}

These errors are all handled in the common.py as Flask exception handlers
"""

class ApiException(Exception):
    """Base class of all exceptions that the API throws. This class should be rarely used
    and a specific child should be raised"""
    missing_fields = 'missing_fields'
    already_exists = 'already_exists'
    storage_error = 'storage_error'
    not_found = 'not_found'
    unknown_error = 'unknown_error'

    def __init__(self, status_code : int, error_code : str, description : str):
        super().__init__()
        self.status_code = status_code
        self.error_code = error_code
        self.description = description

class MissingFieldsException(ApiException):
    """When some required fields are missing in the API call"""
    def __init__(self, fields : t.List[FormField]):
        super().__init__(UnprocessableEntity.code, ApiException.missing_fields, 'Values for some input fields are missing')
        self.fields = fields

class AlreadyExistsException(ApiException):
    """When a resource already exists"""
    def __init__(self, description : str):
        super().__init__(Conflict.code, ApiException.already_exists, description)

class NotFoundException(ApiException):
    """When a resource should have existed but was not found"""
    def __init__(self, description : str):
        super().__init__(Gone.code, ApiException.not_found, description)

class StorageException(ApiException):
    """An exception that is used to indicate some kind of issue with the storage engine"""
    def __init__(self, support_id : int):
        super().__init__(507, ApiException.storage_error, 
            f'An error occurred during saving values. Support ID = {support_id}')
