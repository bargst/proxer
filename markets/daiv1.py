from flask import Blueprint, jsonify, current_app
from flask.views import MethodView

from .pymaker.pymaker import Address
from .pymaker.pymaker.sai import Tub

dai_tub = '0x448a5065aeBB8E423F0896E6c5D525C040f59af3'

daiv1_api = Blueprint('daiv1_api', __name__)

class DAIv1:

    def __init__(self, web3):
        self.tub = Tub(web3=web3, address=Address(dai_tub))

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


class DAIv1Cup(MethodView):

    def get(self, cup_id):
        dai = current_app.extensions['daiv1']
        return jsonify(dai.get_cup(cup_id))
daiv1_api.add_url_rule('/cups/<int:cup_id>', view_func=DAIv1Cup.as_view('cup'))


class DAIv1Cups(MethodView):

    def get(self):
        dai = current_app.extensions['daiv1']
        return jsonify(dai.get_cups())
daiv1_api.add_url_rule('/cups', view_func=DAIv1Cups.as_view('cups'))


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
