from flask import Blueprint, jsonify, request, abort
from flask.views import MethodView

from .utils import web3, tokens, cast_addr


token_api = Blueprint('token_api', __name__)


@token_api.route("/")
def get_tokens():
    return jsonify({ name: str(tokens[name].address) for name in tokens})

class Token(MethodView):

    def get(self, account_id, token, addr):
        address = cast_addr(account_id)
        spender = cast_addr(addr)
        if not address:
            return jsonify({})

        if token:
            if token in tokens:
                token_list = [(token, tokens[token])]
            else:
                abort(404)
        else:
            token_list = tokens.items()


        t = {}
        for name, token in token_list:
            balance = token.functions.balanceOf(address).call()
            allowance = 0
            if spender:
                allowance = token.functions.allowance(address, spender).call()
            t[name] = {}
            if balance or allowance:
                t[name]['balance'] = balance
            if allowance or spender:
                t[name]['allowance'] = allowance
            if not t[name]:
                t.pop(name)
            else:
                t[name]['address'] = token.address


        return jsonify(t)

    def put(self, account_id, token, addr):
        src = cast_addr(account_id)
        dst = cast_addr(addr)
        if not src:
            abort(404)

        if not token or token not in tokens:
            abort(404)
        t = tokens[token].functions

        # ['transfer', 'transferFrom', 'approve']
        req_json = request.get_json()
        transaction = {}
        if req_json and 'transfert' in req_json and dst:
            amount = req_json['transfert']
            try:
                tx = t.transfer(dst, amount).buildTransaction()
            except:
                tx = {}
            return jsonify(tx)

        if req_json and 'transferFrom' in req_json and dst:
            amount = req_json['transferFrom']
            try:
                tx = t.transferFrom(dst, amount).buildTransaction()
            except:
                tx = {}
            return jsonify(tx)

        if req_json and 'approve' in req_json and dst:
            amount = req_json['approve']
            try:
                tx = t.approve(dst, amount).buildTransaction()
            except:
                tx = {}
            return jsonify(tx)

        if req_json and 'deposit' in req_json and token in ['OWETH', 'WETH']:
            amount = req_json['deposit']
            try:
                tx = t.deposit().buildTransaction()
                tx['value'] = amount
            except:
                tx = {}
            return jsonify(tx)

        if req_json and 'withdraw' in req_json and token in ['OWETH', 'WETH']:
            amount = req_json['withdraw']
            tx = t.withdraw(amount).buildTransaction({'gas':150000})
            return jsonify(tx)

        return jsonify({})

token_view = Token.as_view('tokens')
token_api.add_url_rule('/<account_id>', defaults={'token': None, 'addr': None}, view_func=token_view)
token_api.add_url_rule('/<account_id>/<token>', defaults={'addr': None}, view_func=token_view)
token_api.add_url_rule('/<account_id>/<token>/<addr>', view_func=token_view)
