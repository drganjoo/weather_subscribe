import typing as t
from werkzeug.exceptions import UnprocessableEntity
from .commontypes import FormField

class ApiException(Exception):
    missing_fields = "missing_fields"
    already_exists = "already_exists"

    def __init__(self, status_code : int, error_code : str, description : str):
        self.status_code = status_code
        self.error_code = error_code
        self.description = description

class MissingFieldsException(ApiException):
    def __init__(self, fields : t.List[FormField]):
        super().__init__(self, UnprocessableEntity.code, ApiException.missing_fields, "Values for some input fields are missing")
        self.fields = fields

class AlreadyExistsException(ApiException):
    def __init__(self, description):
        super().__init__(self, ApiException.already_exists, description)
