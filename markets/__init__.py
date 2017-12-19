from flask import Flask, Blueprint
from markets.oasis import OasisBook, OasisMarket
from markets.daiv1 import DAIv1Cups, DAIv1

oasis_api = Blueprint('oasis_api', __name__)
oasis_api.add_url_rule('/book', view_func=OasisBook.as_view('book'))

daiv1_api = Blueprint('daiv1_api', __name__)
daiv1_api.add_url_rule('/cups', view_func=DAIv1Cups.as_view('cups'))

markets_app = Flask(__name__)
markets_app.register_blueprint(oasis_api, url_prefix='/oasis')
markets_app.register_blueprint(daiv1_api, url_prefix='/daiv1')

def app_push_web3(app, web3):
    app.extensions['web3'] = web3
    app.extensions['oasis_market'] = OasisMarket(web3)
    app.extensions['daiv1'] = DAIv1(web3)
