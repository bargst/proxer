from flask import url_for
import pytest
import json
from manager import manager_app
from markets import markets_app, app_push_web3

from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider

from markets.pymaker.pymaker.deployment import Deployment

def to_json(resp):
    return json.loads(resp.data)

@pytest.fixture
def manager():
    return manager_app.test_client()

@pytest.fixture
def markets():
    deployment = Deployment()
    app_push_web3(markets_app, deployment.web3)
    return markets_app.test_client()

account_addr = '0xaF63264Ff89Aa82b4d325477dBeEdCe3Cf827552'
account_keyfile = {'address': 'af63264ff89aa82b4d325477dbeedce3cf827552', 'crypto': {'cipher': 'aes-128-ctr', 'ciphertext': 'da9cb944aeb626fe4e353eb6f392984c7d81f98b6c971ce5c6f192b9425afcef', 'cipherparams': {'iv': '7a7a41fa41b1c2c2cdb8193fefa1a4d0'}, 'kdf': 'scrypt', 'kdfparams': {'dklen': 32, 'n': 262144, 'p': 1, 'r': 8, 'salt': 'dd12ffb0ee62ec4ed304572e308854c22c907a10cf5ad75a799d7dac7b57ba38'}, 'mac': '9815484fd13890521567f8aa069a668da1df102c11483d7847f9ed6ca30a9b84'}, 'id': '9cf8212a-0c6d-4770-a1c0-54e67b964d58', 'version': 3}

class TestAccounts:

    def test_get_accounts(self, markets, manager):
        assert to_json(markets.get('/accounts')) == {}

        # Add an account
        addr = to_json(manager.post('/account/', data=json.dumps(account_keyfile), content_type='application/json'))
        assert to_json(markets.get('/accounts')) == { 'web3' : [{'address' : addr}] }
