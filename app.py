from flask import Flask
from flask_migrate import Migrate
import os

# создание экземпляра приложения
app = Flask(__name__)
app.config.from_object('config.BaseConfig')

# инициализирует расширения
migrate = Migrate(app)

import views