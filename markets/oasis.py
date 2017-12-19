from flask import Blueprint, jsonify, current_app
from flask.views import MethodView

from .pymaker.pymaker import Address
from .pymaker.pymaker.oasis import MatchingMarket

oasis_addr = '0x14FBCA95be7e99C15Cc2996c6C9d841e54B79425'
weth_addr  = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
dai_addr   = '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359'

oasis_api = Blueprint('oasis_api', __name__)

class OasisMarket:

    def __init__(self, web3):
        self.base = Address(weth_addr)
        self.quote = Address(dai_addr)
        self.oasis = MatchingMarket(web3=web3, address=Address(oasis_addr))

    def cast_order(self, order):
        sell_amount = order.pay_amount
        sell_token = order.pay_token
        buy_amount = order.buy_amount
        buy_token  = order.buy_token
        oid = order.order_id

        side = None
        casted_order = {}

        # price = quote/base
        if sell_token == self.base and buy_token == self.quote:
            side = 'asks'
            casted_order = {
                'price': float(order.buy_to_sell_price),
                'amount': float(sell_amount),
                'id': oid,
                }
        if sell_token == self.quote and buy_token == self.base:
            side = 'bids'
            casted_order = {
                'price': float(order.sell_to_buy_price),
                'amount': float(sell_amount),
                'id': oid,
                }

        return (side, casted_order)

    def get_orders(self):
        #TODO use filter to update book
        depth = {}
        depth['bids'] = []
        depth['asks'] = []
        for order in self.oasis.get_orders():
            (side, order) = self.cast_order(order)
            if side:
                depth[side].append(order)

        depth['asks'].sort(key=lambda order: order['price'], reverse=True)
        depth['bids'].sort(key=lambda order: order['price'], reverse=True)
        return depth


class OasisBook(MethodView):

    def get(self):
        oasis_market = current_app.extensions['oasis_market']
        return jsonify(oasis_market.get_orders())

oasis_api.add_url_rule('/book', view_func=OasisBook.as_view('book'))

