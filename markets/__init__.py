from flask import Flask, jsonify, request
import copy

class MarketsAPI(object):

    def __init__(self):
        self.markets = {}
        self.app = Flask(__name__)
        self.add_routes()

    def add_market(self, name, api):
        self.markets[name] = api

    # Flask decorator in a class ...
    def add_routes(self):
        self.app.route('/')(self.get_markets)
        self.app.route('/<market>')(self.get_market)
        self.app.route('/<market>/book')(self.get_book)

    def get_markets(self):
        return jsonify(list(self.markets.keys()))

    def get_market(self, market):
        market_api = self.markets[market]
        return jsonify(str(market_api))

    def get_book(self, market):
        market_api = self.markets[market]
        return jsonify(market_api.get_book())
