import os
from flask import Flask

app = Flask(__name__, instance_relative_config = True)

def load_config(app, test_config=None):
    # default configuration
    app.config.from_mapping(
        DATABASE_URI = 'postgresql://apiadmin:passw0rd@localhost/weather_api',
        API_KEY = '5b77b80f14e25b799dbd2f4ea8616a62'
    )

    # ensure the instance folder exists, this would just help keep
    # production configuration separate 
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # load config from the config.py file, if one exists
    if test_config is None:
        print('loading configuration from config.py file')
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

