import requests

from .pymaker.pymaker import Address
from .pymaker.pymaker.oasis import MatchingMarket

class API(object):

    def __init__(self, web3, oasis_addr, base_token, quote_token):
        self.web3 = web3
        self.base = Address(base_token)
        self.quote = Address(quote_token)
        self.oasis = MatchingMarket(web3=self.web3, address=Address(oasis_addr))
        self.depth = {}
        self.depth['bids'] = []
        self.depth['asks'] = []
        self.from_block = ''

    def update_depth(self, order):
        # Remove oid from depth before, re-add it if active
        oid = order.order_id
        asks = [ order for order in self.depth['asks'] if order['id'] != oid]
        bids = [ order for order in self.depth['bids'] if order['id'] != oid]

        sell_amount = order.pay_amount
        sell_token = order.pay_token
        buy_amount = order.buy_amount
        buy_token  = order.buy_token

        # price = quote/base
        if sell_token == self.base and buy_token == self.quote:
            asks.append({
                'price': float(order.buy_to_sell_price),
                'amount': float(sell_amount),
                'id': oid,
                })
        if sell_token == self.quote and buy_token == self.base:
            bids.append({
                'price': float(order.sell_to_buy_price),
                'amount': float(sell_amount),
                'id': oid,
                })

        self.depth['asks'] = asks
        self.depth['bids'] = bids
        self.depth['asks'].sort(key=lambda order: order['price'])
        self.depth['bids'].sort(key=lambda order: order['price'])

    def get_book(self):
        #TODO use filter to update book
        for order in self.oasis.get_orders():
            self.update_depth(order)
        return self.depth
