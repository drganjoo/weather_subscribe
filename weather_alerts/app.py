import os
import shutil
from flask import Flask

app = Flask(__name__, instance_relative_config = True)

def load_config(app, test_config=None):
    # default configuration
    app.config.from_mapping(
        DATABASE_URI = 'postgresql://apiadmin:passw0rd@localhost/weather_api',
        API_KEY = ''
    )

    # ensure the instance folder exists, this would just help keep
    # production configuration separate 
    if not os.path.exists(app.instance_path):
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass
    
    config_file = f'{app.instance_path}/config.py'
    if not os.path.exists(config_file):
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'config.py'), config_file)

    # load config from the config.py file, if one exists
    if test_config is None:
        print('loading configuration from config.py file')
        app.config.from_pyfile('config.py', silent=False)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

