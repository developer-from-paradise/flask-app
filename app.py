from flask import Flask
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import logging

# создание экземпляра приложения
app = Flask(__name__)
app.config.from_object('config.BaseConfig')
app.wsgi_app = ProxyFix(app.wsgi_app)


# # Logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'error.log')
root_logger= logging.getLogger()
root_logger.setLevel(logging.ERROR)
handler = logging.FileHandler(log_file, 'w', 'utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(handler)



# инициализирует расширения
migrate = Migrate(app)

import views