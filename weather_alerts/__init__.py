# Project description:
# Develop a Rest API with endpoints for weather alert subscriptions. A subscription 
# has an email address, a location (e.g. city) and some simple weather conditions to 
# be alerted about, (e.g. temperature less than 0 celsius).
from flask import Flask
from weather_alerts.database import db_session, init_db

app = Flask(__name__, instance_relative_config = True)

@app.teardown_appcontext
def shutdown_session(exception=None):
    print('shutdown_session fired')
    db_session.remove()

# app.config.from_mapping(
#     API_KEY='5b77b80f14e25b799dbd2f4ea8616a62',
#     SQLALCHEMY_DATABASE_URI = 'postgresql://apiadmin:passw0rd@localhost/weather_api'
# )

# if test_config is None:
#     app.config.from_pyfile('config.py', silent = True)
# else:
#     app.config.from_mapping(test_config)

@app.route("/")
def index():
    return "hi there"

@app.route("/check_db")
def check_db():
    db = get_db()
    with db.connect() as conn:
        result = conn.execute(text("select 'hello'"))
        all = result.all()
        print(all[0])
        return all[0][0]

@app.cli.command("init-db")
def command_init_db():
    """Clear the existing data and create new tables."""
    init_db()
    print('Database has been created')