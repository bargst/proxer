from flask import jsonify, current_app
from flask.views import MethodView

from .pymaker.pymaker import Address
from .pymaker.pymaker.oasis import MatchingMarket

oasis_addr = '0x3Aa927a97594c3ab7d7bf0d47C71c3877D1DE4A1'
weth_addr  = '0xECF8F87f810EcF450940c9f60066b4a7a501d6A7'
sai_addr   = '0x59aDCF176ED2f6788A41B8eA4c4904518e62B6A4'

class OasisMarket:

    def __init__(self, web3):
        self.base = Address(weth_addr)
        self.quote = Address(sai_addr)
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
            (side, order) = cast_order(order)
            if side:
                depth[side].append(order)

        depth['asks'].sort(key=lambda order: order['price'], reverse=True)
        depth['bids'].sort(key=lambda order: order['price'], reverse=True)
        return depth


class OasisBook(MethodView):

    def get(self):
        oasis_market = current_app.extensions['oasis_market']
        return jsonify(oasis_market.get_orders())
