import typing as t
from werkzeug.exceptions import HTTPException
from .database import db_session
from .exceptions import ApiException, MissingFieldsException
import flask
from .commontypes import FormField, FormFieldList

def register_pre_post(app: flask.Flask):
    # todo: check how to close the connection
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        print('shutdown_session fired')
        db_session.remove()

    @app.errorhandler(ApiException)
    def handle_api_exception(e : ApiException) -> t.Dict[str, t.Any]:
        """A JSON object that displays proper error object"""
        return {
            "error": {
                "code": e.error_code,
                "description" : e.description
            }
         }, e.status_code

    @app.errorhandler(MissingFieldsException)
    def handle_missing_fields(e : MissingFieldsException):
        """Return a list of all missing fields"""
        json_dict = handle_api_exception(e)
        json_dict.error["fields"] = [f.name for f in e.fields]

        return json_dict


    @app.errorhandler(HTTPException)
    def handle_exception(e : HTTPException):
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

    @app.errorhandler(Exception)
    def handle_exception(e : Exception):
        """Convert exception into a proper JSON format"""
        return { "error": {
                    "code": e.code,
                    "description": str(e)
            }
        }

    @app.after_request
    def add_headers(resp : flask.Response) -> flask.Response:
        resp.headers['X-Api-Ver'] = '1.0'
        return resp

def get_fields(request : flask.request, fields: FormFieldList):
    missing_fields : t.List[FormField] = []
    field_values : t.Dict[str, str] = {}

    form_input_values : t.Optional[t.Any] = request.get_json(force=True)

    if form_input_values == None:
        raise MissingFieldsException(missing_fields)

    f : FormField
    for f in fields:
        # raise an exception in case the field is required but not present in the form
        if f.name not in form_input_values and f.is_required:
            missing_fields.append(f)
        else:
            field_values[f.name] = form_input_values[f.name]
            
    if len(missing_fields) > 0:
        raise MissingFieldsException(missing_fields)

    print(field_values)
    return field_values