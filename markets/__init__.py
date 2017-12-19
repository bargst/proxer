from flask import Flask, Blueprint
from markets.oasis import OasisBook, OasisMarket

oasis_api = Blueprint('oasis_api', __name__)
oasis_api.add_url_rule('/book', view_func=OasisBook.as_view('book'))

markets_app = Flask(__name__)
markets_app.register_blueprint(oasis_api, url_prefix='/oasis')
