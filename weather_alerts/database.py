import sys
import typing as t
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .app import app

# figure out the URI from the app object
uri : str = app.config['DATABASE_URI']
if uri is None:
    print('DATABASE_URI is not set in app config')
    sys.exit(-1)

print(f'Using database uri: {uri}')
try:
    engine = create_engine(uri)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
except Exception as e:
    print('Error occurred connecting to the database. Error: {e}')
    sys.exit(-2)

Base = declarative_base()
Base.query = db_session.query_property()

def register_commands(app : Flask):
    """All commands that can be run on the database from the command line
    by using flask {cmd} are registered through this function"""

    @app.cli.command("init-db")
    def init_db():
        """Creates a new database"""
        from . import models
        Base.metadata.create_all(bind=engine)