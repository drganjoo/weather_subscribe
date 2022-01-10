from flask import Flask, Blueprint
from weather_alerts.database import db_session
from sqlalchemy.exc import OperationalError

"""A health route to be used internally  to check the health of the service"""

bp = Blueprint('health', __name__, url_prefix='/health')

@bp.route("/")
def health():
    try:
        result = db_session.execute("select version()")
        r = result.fetchone()
        # todo: get version from the package rather than hard code
        return {
            "appVersion": "1.0",
            "dbVersion": r[0]
        } 
    except OperationalError as e:
        return {
            "error": f'An error occurred, error: {e}'
        }, 501
    except Exception as e:
        return {
            "error": f'An error occurred, error: {e}'
        }, 500

def register_routes(app : Flask):
    # register the blueprint for health with the given app
    app.register_blueprint(bp)