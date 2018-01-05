from flask import Blueprint, jsonify, current_app
from flask.views import MethodView

from .pymaker.pymaker import Address
from .pymaker.pymaker.numeric import Wad
from .pymaker.pymaker.sai import Tub, Tap

daiv1_api = Blueprint('daiv1_api', __name__)

class DAIv1:

    def __init__(self, web3, dai_tub = '0x448a5065aeBB8E423F0896E6c5D525C040f59af3'):
        self.tub = Tub(web3=web3, address=Address(dai_tub))
        self.tap = Tap(web3=web3, address=self.tub.tap())
        self.tokens = {
                'MKR': self.tub.gov(),
                'PETH': self.tub.skr(),
                'WETH': self.tub.gem(),
                'DAI': self.tub.sai(),
        }

    def get_cup(self, cup_id):
        cup = self.tub.cups(cup_id)
        return { 'id': cup.cup_id,
                'lad': cup.lad.address,
                'art': float(cup.art),
                'ink': float(cup.ink),
                'safe': self.tub.safe(cup_id)
               }

    def get_cups(self):
        last_cup_id = self.tub.cupi()
        cups = map(self.get_cup, range(1, last_cup_id+1))
        not_empty_cups = filter(lambda cup: cup['lad'] != "0x0000000000000000000000000000000000000000", cups)
        return list(not_empty_cups)

    def get_pairs(self):
        pairs = ['PETH/DAI', 'PETH/WETH']
        return pairs

    def get_orders(self, base, quote):
        depth = {'bids': [], 'asks': []}

        # PETH/DAI order book
        if base == 'PETH' and quote == 'DAI':
            # boom is a taker using a bid side from maker tap
            # a taker convert PETH to DAI using tap.bid(1) as price
            # maker side offer DAI in exchange for PETH (flap)
            # DAI qty offered by is min(joy - woe, 0)
            order = { 'price': float(self.tap.bid(Wad.from_number(1))),
                      'amount': float(min(self.tap.joy() - self.tap.woe(), Wad.from_number(0))),
                      'id': 'take:tap.boom()',
                    }
            if order['amount'] > 0:
                depth['bids'].append(order)

            # bust is a taker using ask side from maker tap
            # a taker convert DAI to PETH using tap.ask(1) as price
            # maker side offer PETH from fog (flip) and PETH minted to cover woe (flop)
            # PETH qty offered by maker is fog+min(woe-joy, 0)/ask
            order = { 'price': float(self.tap.ask(Wad.from_number(1))),
                      'amount': float(self.tap.fog() + min(self.tap.woe() - self.tap.joy(), Wad.from_number(0)) / self.tap.ask(Wad.from_number(1))),
                      'id': 'take:tap.bust()',
                    }
            if order['amount'] > 0:
                depth['asks'].append(order)

        # PETH/WETH order book
        if base == 'PETH' and quote == 'WETH':
            # exit is a taker using a bid side from maker tub
            # a taker PETH to WETH using tub.bid(1) as price
            # maker side offer WETH in exchange for PETH
            # WETH qty offered by maker is infinity (2**32 as a large number for infinity ...)
            order = { 'price': float(self.tub.bid(Wad.from_number(1))),
                      'amount': float(2**32),
                      'id': 'take:tub.exit()',
                    }
            depth['bids'].append(order)

            # join is a taker using ask side from maker tub
            # a taker convert WETH to PETH usgin tub.ask(1) as price
            # maker side offer PETH in exchange for WETH
            # PETH qty offered by maker is infinity (2**32 as a large number for infinity ...)
            order = { 'price': float(self.tub.ask(Wad.from_number(1))),
                      'amount': float(2**32),
                      'id': 'take:tub.join()',
                    }
            depth['asks'].append(order)

        return depth


class DAIv1Cup(MethodView):

    def get(self, cup_id):
        dai = current_app.extensions['daiv1']
        if cup_id:
            cups = dai.get_cup(cup_id)
        else:
            cups = dai.get_cups()
        return jsonify(cups)
cup_view = DAIv1Cup.as_view('cup')
daiv1_api.add_url_rule('/cups', defaults={'cup_id': None}, view_func=cup_view)
daiv1_api.add_url_rule('/cups/<int:cup_id>', view_func=cup_view)

class DAIv1Tub(MethodView):

    def get(self):
        dai = current_app.extensions['daiv1']
        tub_details = {
                'cap': float(dai.tub.cap()),
                'mat': float(dai.tub.mat()),
                'tax': float(dai.tub.tax()),
                'chi': float(dai.tub.chi()),
                'din': float(dai.tub.din()),
                'tag': float(dai.tub.tag()),
                'per': float(dai.tub.per()),
                'gap': float(dai.tub.gap()),
        }
        return jsonify(tub_details)
daiv1_api.add_url_rule('/', view_func=DAIv1Tub.as_view('tub'))

class DAIv1Book(MethodView):

    def get(self, base, quote):
        dai = current_app.extensions['daiv1']
        if f'{base}/{quote}' in dai.get_pairs():
            book = dai.get_orders(base, quote)
        else:
            book = {'bids': [], 'asks': []}
        return jsonify(book)

book_view = DAIv1Book.as_view('book')
#daiv1_api.add_url_rule('/book', defaults={'base': 'PETH', 'quote': 'WETH'}, view_func=book_view)
daiv1_api.add_url_rule('/book/<base>/<quote>', view_func=book_view)

class DAIv1Pairs(MethodView):

    def get(self):
        dai = current_app.extensions['daiv1']
        return jsonify(dai.get_pairs())

daiv1_api.add_url_rule('/pairs', view_func=DAIv1Pairs.as_view('pairs'))
