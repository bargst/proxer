from flask import Flask
from manager.account import account_api

manager_app = Flask(__name__)
manager_app.register_blueprint(account_api, url_prefix='/account')
