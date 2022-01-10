# Project description:
# Develop a Rest API with endpoints for weather alert subscriptions. A subscription 
# has an email address, a location (e.g. city) and some simple weather conditions to 
# be alerted about, (e.g. temperature less than 0 celsius).
from flask import Flask

from .routes import health, weather
from .database import db_session, register_commands
from . import common

app = Flask(__name__, instance_relative_config = True)

register_commands(app)

common.register_pre_post(app)
weather.register_routes(app)
health.register_routes(app)