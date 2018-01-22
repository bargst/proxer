from flask import Blueprint, jsonify, request
from pymaker import Address

from .utils import web3, tokens


token_api = Blueprint('token_api', __name__)


@token_api.route("/")
def get_tokens():
    return jsonify({ name: str(tokens[name].address) for name in tokens})

@token_api.route('/<account_id>')
def show_tokens(account_id):
    try:
        address = web3.toChecksumAddress(account_id)
    except:
        address = None

    t = {}
    for name, token in tokens.items():
        balance = token.balance_of(Address(address))
        if balance.value:
            t[name] = {
                'balance': balance.value,
            }

    return jsonify(t)
