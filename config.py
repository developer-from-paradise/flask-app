import os
from pathlib import Path
from datetime import timedelta
from cloudflare import CloudFlare

app_dir = os.path.abspath(os.path.dirname(__file__))

salt = 'script:3424/sad8732ubdsjkdbhaskdljsuioahdkjsabdk'

account_id = 'b780405629df43cca324250bc5d3e4c0'
api_key = '94a6d32b704a6b5aacf2c138087078ffbc41f'
email = 'kamazzcha@gmail.com'
server_domain = 'depian.ru'

clf = CloudFlare(email, api_key, account_id)

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A SECRET KEY'
    DEBUG = True
    permanent_session_lifetime = timedelta(minutes=5)