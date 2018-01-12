from flask import Blueprint, jsonify, current_app, url_for
from flask.views import MethodView
import requests

from . import Market

from .pymaker.pymaker import Address
from .pymaker.pymaker.token import ERC20Token
from .pymaker.pymaker.oasis import MatchingMarket

oasis_addr = '0x14FBCA95be7e99C15Cc2996c6C9d841e54B79425'
weth_addr  = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
dai_addr   = '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359'

# Tokens, extracted from :
# https://github.com/OasisDEX/oasis/blob/master/frontend/packages/dapple/config.json
tokens =  {'OWETH': '0xECF8F87f810EcF450940c9f60066b4a7a501d6A7', 'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'DAI': '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359', 'SAI': '0x59aDCF176ED2f6788A41B8eA4c4904518e62B6A4', 'MKR': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2', 'DGD': '0xE0B7927c4aF23765Cb51314A0E0521A9645F0E2A', 'GNT': '0xa74476443119A942dE498590Fe1f2454d7D4aC0d', 'W-GNT': '0x01AfC37F4F85babc47c0E2d0EAbABC7FB49793c8', 'REP': '0xE94327D07Fc17907b4DB788E5aDf2ed424adDff6', 'ICN': '0x888666CA69E0f178DED6D75b5726Cee99A87D698', '1ST': '0xAf30D2a7E90d7DC361c8C4585e9BB7D2F6f15bc7', 'SNGLS': '0xaeC2E87E0A235266D9C5ADc9DEb4b2E29b54D009', 'VSL': '0x5c543e7AE0A1104f78406C340E9C64FD9fCE5170', 'PLU': '0xD8912C10681D8B21Fd3742244f44658dBA12264E', 'MLN': '0xBEB9eF514a379B997e0798FDcC901Ee474B6D9A1', 'RHOC': '0x168296bb09e24A88805CB9c33356536B980D3fC5', 'TIME': '0x6531f133e6DeeBe7F2dcE5A0441aA7ef330B4e53', 'GUP': '0xf7B098298f7C69Fc14610bf71d5e02c60792894C', 'BAT': '0x0D8775F648430679A709E98d2b0Cb6250d2887EF', 'NMR': '0x1776e1F26f98b1A5dF9cD347953a26dd3Cb46671'}

oasis_api = Blueprint('oasis_api', __name__)

class OasisMarket(Market):

    def __init__(self, web3):
        self.web3 = web3
        self.oasis = MatchingMarket(web3=web3, address=Address(oasis_addr))
        self.tokens = {}
        for token in tokens:
            self.tokens[token] = ERC20Token(web3, Address(tokens[token]))
        # Pop GNT because its not an ERC20 token
        self.tokens.pop('GNT')

    def cast_order(self, order, base_addr, quote_addr):
        base = Address(base_addr)
        quote = Address(quote_addr)

        sell_amount = order.pay_amount
        sell_token = order.pay_token
        buy_amount = order.buy_amount
        buy_token  = order.buy_token
        oid = order.order_id

        side = None
        casted_order = {}

        # price = quote/base
        if sell_token == base and buy_token == quote:
            side = 'asks'
            casted_order = {
                'price': float(order.buy_to_sell_price),
                'amount': float(sell_amount),
                'id': oid,
                }
        if sell_token == quote and buy_token == base:
            side = 'bids'
            casted_order = {
                'price': float(order.sell_to_buy_price),
                'amount': float(sell_amount),
                'id': oid,
                }

        return (side, casted_order)

    def get_orders(self, base_addr, quote_addr):
        #TODO use filter to update book
        depth = {}
        depth['bids'] = []
        depth['asks'] = []
        for order in self.oasis.get_orders():
            (side, order) = self.cast_order(order, base_addr, quote_addr)
            if side:
                depth[side].append(order)

        depth['asks'].sort(key=lambda order: order['price'], reverse=True)
        depth['bids'].sort(key=lambda order: order['price'], reverse=True)
        return depth

    def get_pairs(self):
        #TODO use filter to update book
        pairs = []
        addr2token = { tokens[t] : t for t in tokens }
        for order in self.oasis.get_orders():
            sell_token = addr2token[str(order.pay_token)]
            buy_token  = addr2token[str(order.buy_token)]
            pairs.append(f'{sell_token}/{buy_token}')

        # Get uniq paris
        pairs = list(set(pairs))
        return pairs

    def get_accounts(self, manager_url):
        accounts = {}
        for addr in requests.get(manager_url).json():
            accounts[addr] = {
                'balance' : self.web3.eth.getBalance(addr),
            }
            accounts[addr]['tokens'] = {}
            for name, token in self.tokens.items():
                balance = token.balance_of(Address(addr))
                allowance = token.allowance_of(Address(addr), self.oasis.address)
                if float(allowance) or float(balance):
                    accounts[addr]['tokens'][name] = {
                            'allowance': float(allowance),
                            'balance': float(balance),
                    }

        return accounts

class OasisBook(MethodView):

    def get(self, base, quote):
        oasis_market = current_app.extensions['/oasis']
        if base in tokens and quote in tokens:
            book = oasis_market.get_orders(tokens[base], tokens[quote])
        else:
            book = {'bids': [], 'asks': []}
        return jsonify(book)

book_view = OasisBook.as_view('book')
oasis_api.add_url_rule('/book', defaults={'base': 'DAI', 'quote': 'SAI'}, view_func=book_view)
oasis_api.add_url_rule('/book/<base>/<quote>', view_func=book_view)

class OasisPairs(MethodView):

    def get(self):
        oasis_market = current_app.extensions['/oasis']
        return jsonify(oasis_market.get_pairs())

oasis_api.add_url_rule('/pairs', view_func=OasisPairs.as_view('pairs'))
