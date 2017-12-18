from web3 import eth
from flask import Blueprint, jsonify, request
import copy

from web3 import Web3

account_api = Blueprint('account_api', __name__)

accounts = {} 

@account_api.route("/")
def get_accounts():
    return jsonify([ addr for addr in accounts.keys()])

@account_api.route('/', methods=['POST'])
def add_account():
    address = ""

    req_json = request.get_json()

    if req_json and "address" in req_json:
        address = Web3.toChecksumAddress(req_json["address"])
        accounts[address] = { "locked": True }
        accounts[address]["key_file"] = req_json

    return jsonify(address)

@account_api.route('/<account_id>')
def show_account(account_id):
    try:
        address = Web3.toChecksumAddress(account_id)
    except:
        address = None
    account = {}

    if address in accounts.keys():
        # Doing a deepcopy to avoid poping "private_key" ...
        account = copy.copy(accounts[address])
        if "key_file" in account:
            account.pop("key_file")
        if "private_key" in account:
            account.pop("private_key")
        
    return jsonify(account)

@account_api.route('/<account_id>', methods=['POST'])
def unlock(account_id):
    try:
        address = Web3.toChecksumAddress(account_id)
    except:
        address = None
    password = ""

    req_json = request.get_json()
    if req_json and "password" in req_json:
        password = req_json["password"]

    # Force Lock with empty password
    if not password:
        accounts[address]["private_key"] = ""
        accounts[address]["locked"] = True

    # Try to unlock key_file
    if address in accounts.keys() and password:
        try:
            accounts[address]["private_key"] = eth.Account.decrypt(accounts[address]["key_file"], password)
            accounts[address]["locked"] = False
        except :
            accounts[address]["private_key"] = ""
            accounts[address]["locked"] = True

    return show_account(address)

# Sign
# >>> transaction = {
#        'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
#        'value': 1000000000,
#        'gas': 2000000,
#        'gasPrice': 234567897654321,
#        'nonce': 0,
#        'chainId': 1
#    }
# >>> message = {
#        'text': 'test'
#        'message': b'test',
#        'hexstr': '0x736f6d652d746578742d74c3b62d7369676e',
#    }
@account_api.route('/<account_id>', methods=['PUT'])
def sign(account_id):
    try:
        address = Web3.toChecksumAddress(account_id)
    except:
        address = None
    transaction = {}
    key = ""
    signature = ""
    
    if address in accounts and "private_key" in accounts[address]:
        key = accounts[address]["private_key"]

    req_json = request.get_json()

    if key and req_json:

        # Sign message
        if   'message' in req_json:
            signed = eth.Account().sign(message=req_json['message'], private_key=key)
            signature = Web3.toHex(signed.signature)
        elif 'text' in req_json:
            signed = eth.Account().sign(message_text=req_json['text'], private_key=key)
            signature = Web3.toHex(signed.signature)
        elif 'hexstr' in req_json:
            signed = eth.Account().sign(message_hexstr=req_json['hexstr'], private_key=key)
            signature = Web3.toHex(signed.signature)

        # Sign transaction
        elif ( "to"        in req_json
           and "value"    in req_json
           and "gas"      in req_json
           and "gasPrice" in req_json
           and "nonce"    in req_json
           and "chainId"  in req_json):
            signed = eth.Account().signTransaction(req_json, key)
            signature = Web3.toHex(signed.rawTransaction)

    return jsonify(signature)
