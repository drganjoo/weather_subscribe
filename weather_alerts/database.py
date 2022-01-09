import typing as t
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://apiadmin:passw0rd@localhost/weather_api')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

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