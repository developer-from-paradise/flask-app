import os
from pathlib import Path
from datetime import timedelta


app_dir = os.path.abspath(os.path.dirname(__file__))

salt = 'script:3424/sad8732ubdsjkdbhaskdljsuioahdkjsabdk'



class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A SECRET KEY'
    DEBUG = True
    permanent_session_lifetime = timedelta(minutes=5)