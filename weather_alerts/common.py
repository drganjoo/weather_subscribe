import flask
import typing as t
from flask.wrappers import Response
from werkzeug.exceptions import HTTPException
from .logger import Logger
from .database import db_session
from .exceptions import ApiException, MissingFieldsException, StorageException
from .commontypes import FormField, FormFieldList, FormFieldValues
from sqlalchemy.exc import DatabaseError

log = Logger(__name__)

def register_pre_post(app: flask.Flask):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.errorhandler(ApiException)
    def handle_api_exception(e : ApiException) -> t.Tuple[t.Dict[str, t.Any], int]:
        """Any API exception that occurs in the routes, is converted to a JSON object 
        that has a code (identifier) and a description"""
        return {
            "error": {
                "code": e.error_code,
                "description" : e.description
            }
         }, e.status_code

    @app.errorhandler(MissingFieldsException)
    def handle_missing_fields(e : MissingFieldsException) -> t.Tuple[t.Dict[str, t.Any], int]:
        """Return a list of all missing fields"""
        (json_dict, status_code) = handle_api_exception(e)
        error : t.Dict[str, str] = json_dict["error"]

        f : FormField
        error["fields"] = [f.name for f in e.fields]

        return json_dict, status_code

    @app.errorhandler(HTTPException)
    def handle_exception(e : HTTPException) -> t.Tuple[Response, int]:
        """Convert exception into a proper JSON format"""
        response = e.get_response()
        response.data = flask.json.dumps({
            "error": {
                "code": e.code,
                "description": e.description,
            }
        })
        response.content_type = "application/json"

        return response, e.code

    @app.errorhandler(DatabaseError)
    def handle_exception(e : DatabaseError):
        """All database related errors are never shown to the user. A unique support ID is created
        and that is sent back"""
        # create a support ID and throw a Storage exception that will be dealt
        # by the generic exception handler
        support_id = log.error(str(e))
        raise StorageException(support_id)

    @app.errorhandler(Exception)
    def handle_exception(e : Exception) -> t.Tuple[t.Dict[str, t.Any], int]:
        """Till development any general exception will be sent back but in production this too
        should only send back a support ID"""
        return { 
            "error": {
                "code": ApiException.unknown_error,
                "description": str(e)
            }
        }, 501

    @app.after_request
    def add_headers(resp : flask.Response) -> flask.Response:
        """Generic headers that should be present in all responses"""
        resp.headers['X-Api-Ver'] = '1.0'
        return resp

def get_fields(request : flask.request, fields: FormFieldList) -> t.List[str]:
    """Looks in the passed in request and returns all fields that the caller has requested.
    In case a field does not have a value and it is a mandatory field, an exception will be 
    raised, otherwise None will be returned in its place. All missing fields are returned as
    a list in the exception."""
    missing_fields : t.List[FormField] = []
    field_values : t.List[str] = []

    # get incoming JSON from the body  of the request and raise an exception in 
    # case the body cannot be found
    form_input_values : t.Optional[t.Any] = request.get_json(force=True)
    if form_input_values == None:
        raise MissingFieldsException(missing_fields)

    f : FormField
    for f in fields:
        # raise an exception in case the field is required but not present in the form
        if f.name not in form_input_values:
            if f.is_required:
                missing_fields.append(f)
            else:
                field_values.append(None)
        else:
            field_values.append(form_input_values[f.name])
    
    # any missing fields? raise a MissinFieldException
    if len(missing_fields) > 0:
        raise MissingFieldsException(missing_fields)

    return field_values