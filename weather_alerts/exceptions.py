import typing as t
from werkzeug.exceptions import UnprocessableEntity, Conflict
from .commontypes import FormField

class ApiException(Exception):
    missing_fields = 'missing_fields'
    already_exists = 'already_exists'
    storage_error = 'storage_error'
    unknown_error = 'unknown_error'

    def __init__(self, status_code : int, error_code : str, description : str):
        super().__init__()
        self.status_code = status_code
        self.error_code = error_code
        self.description = description

class MissingFieldsException(ApiException):
    def __init__(self, fields : t.List[FormField]):
        super().__init__(UnprocessableEntity.code, ApiException.missing_fields, 'Values for some input fields are missing')
        self.fields = fields

class AlreadyExistsException(ApiException):
    def __init__(self, description : str):
        super().__init__(Conflict.code, ApiException.already_exists, description)

class StorageException(ApiException):
    def __init__(self, support_id : int):
        super().__init__(507, ApiException.storage_error, 
            f'An error occurred during saving values. Support ID = {support_id}')
