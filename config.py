import os

from datetime import timedelta
from cloudflare import CloudFlare


salt = 'script:3424/sad8732ubdsjkdbhaskdljsuioahdkjsabdk'
account_id = 'b780405629df43cca324250bc5d3e4c0'
api_key = '94a6d32b704a6b5aacf2c138087078ffbc41f'
email = 'kamazzcha@gmail.com'
# server_domain = 'depian.ru'
server_domain = '10.12.172.172'
server_ip = '5.181.109.172'

clf = CloudFlare(email, api_key, account_id)


app_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A SECRET KEY'
    DEBUG = True
    permanent_session_lifetime = timedelta(minutes=5)
