from flask import jsonify, current_app
from flask.views import MethodView

from .pymaker.pymaker import Address
from .pymaker.pymaker.sai import Tub

dai_tub = '0x448a5065aeBB8E423F0896E6c5D525C040f59af3'

class DAIv1:

    def __init__(self, web3):
        self.tub = Tub(web3=web3, address=Address(dai_tub))

    def get_cups(self):
        last_cup_id = self.tub.cupi()
        cups = map(self.tub.cups, range(1, last_cup_id+1))
        return list(map(str, cups))

class DAIv1Cups(MethodView):

    def get(self):
        dai = current_app.extensions['daiv1']
        return jsonify(dai.get_cups())
