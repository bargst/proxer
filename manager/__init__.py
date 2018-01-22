from flask import Flask
from manager.account import account_api
from manager.token import token_api

manager_app = Flask(__name__)
manager_app.register_blueprint(account_api, url_prefix='/accounts')
manager_app.register_blueprint(token_api, url_prefix='/tokens')
