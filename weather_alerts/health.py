from flask import Flask, Blueprint
from weather_alerts.database import db_session
from sqlalchemy.exc import OperationalError

bp = Blueprint('health', __name__, url_prefix='/health')

@bp.route("/")
def health():
    try:
        result = db_session.execute("select version()")
        r = result.fetchone()
        return {
            "appVersion": "1.0",
            "dbVersion": r[0]
        } 
    except OperationalError as e:
        return {
            "error": f'An error occurred, error: {e}'
        }, 501

def register_routes(app : Flask):
    app.register_blueprint(bp)