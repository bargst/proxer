from flask import Flask, jsonify, current_app

class Market:
    def get_accounts(self, manager_url):
        return {}

from markets.oasis import oasis_api, OasisMarket
from markets.daiv1 import daiv1_api, DAIv1

# Function to define global and persistant market object
def app_push_web3(app, web3):
    app.extensions['web3'] = web3
    app.extensions['/oasis'] = OasisMarket(web3)
    app.extensions['/daiv1'] = DAIv1(web3)

markets = {
    '/oasis': oasis_api,
    '/daiv1': daiv1_api,
}

markets_app = Flask(__name__)
for market in markets:
    markets_app.register_blueprint(markets[market], url_prefix=market)

@markets_app.route('/')
def get_markets():
    return jsonify(list(markets.keys()))

manager_url = 'http://localhost:5000/account/'
@markets_app.route('/accounts')
def get_accounts():
    accounts = {}
    for m in markets:
        accounts[m] = current_app.extensions[m].get_accounts(manager_url)

    return jsonify({'manager_url': manager_url, 'accounts': accounts})
