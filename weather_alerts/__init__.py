# Project description:
# Develop a Rest API with endpoints for weather alert subscriptions. A subscription 
# has an email address, a location (e.g. city) and some simple weather conditions to 
# be alerted about, (e.g. temperature less than 0 celsius).
from .app import app, load_config
load_config(app)

from . import common
from .routes import health, subscribe
from .database import register_commands
from .services.backgroundjobs import sched, setup_jobs

register_commands(app)

common.register_pre_post(app)
subscribe.register_routes(app)
health.register_routes(app)

setup_jobs(interval_seconds = 10)

sched.start()
