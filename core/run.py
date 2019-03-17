# -*- coding: utf-8 -*-
from app.api import create_app
from config import Development, Production
import os

environment = {'development': Development, 'production': Production}
Config = environment[os.environ['FLASK_ENV']]

app = create_app(Config)

if __name__ == '__main__':
    app.run(port=5001, host='0.0.0.0')
