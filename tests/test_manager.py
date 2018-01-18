import pytest
import json
from manager import manager_app

@pytest.fixture
def app():
    app = manager_app
    return app

account_addr = '0xaF63264Ff89Aa82b4d325477dBeEdCe3Cf827552'
account_keyfile = {'address': 'af63264ff89aa82b4d325477dbeedce3cf827552', 'crypto': {'cipher': 'aes-128-ctr', 'ciphertext': 'da9cb944aeb626fe4e353eb6f392984c7d81f98b6c971ce5c6f192b9425afcef', 'cipherparams': {'iv': '7a7a41fa41b1c2c2cdb8193fefa1a4d0'}, 'kdf': 'scrypt', 'kdfparams': {'dklen': 32, 'n': 262144, 'p': 1, 'r': 8, 'salt': 'dd12ffb0ee62ec4ed304572e308854c22c907a10cf5ad75a799d7dac7b57ba38'}, 'mac': '9815484fd13890521567f8aa069a668da1df102c11483d7847f9ed6ca30a9b84'}, 'id': '9cf8212a-0c6d-4770-a1c0-54e67b964d58', 'version': 3}

@pytest.mark.usefixtures('client_class')
class TestAccount:

    def test_empty_manager(self):
        assert self.client.get('/account/',).json == []

    def test_add_invalid_account_keyfile(self):
        res = self.client.post('/account/', data=json.dumps({'qsd': ''})).json
        assert res == ''

    def test_add_valid_account_keyfile(self):
        res = self.client.post('/account/', data=json.dumps(account_keyfile), content_type='application/json')
        assert res.json == account_addr

    def test_show_notempty_account(self):
        res = self.client.get('/account/')
        assert res.json == [ account_addr ]

    def test_show_not_present_account_keyfile(self):
        res = self.client.get(f'/account/0xdead000')
        assert res.json == {}

    def test_show_present_account_keyfile(self):
        res = self.client.get(f'/account/{account_addr}')
        assert res.json['locked'] is True

    def test_unlock_not_present_keyfile(self):
        res = self.client.post(f'/account/0xdead000', data=json.dumps({"password" : "invalid_password"}), content_type='application/json')
        assert res.json == {}

    def test_unlock_keyfile_wrong_password(self):
        res = self.client.post(f'/account/{account_addr}', data=json.dumps({"password" : "invalid_password"}), content_type='application/json')
        assert res.json['locked'] is True

    def test_unlock_keyfile_good_password(self):
        res = self.client.post(f'/account/{account_addr}', data=json.dumps({"password" : "default"}), content_type='application/json')
        assert res.json['locked'] is False

    def test_sign_with_not_present_account(self):
        res = self.client.put(f'/account/0xdead000', data=json.dumps({"text" : "test"}), content_type='application/json')
        assert res.json == ''

    def test_sign_text(self):
        res = self.client.put(f'/account/{account_addr}', data=json.dumps({"text" : "test"}), content_type='application/json')
        assert res.json == '0x802ba60e6c86215a72745a5ca3d5a2b3955f8cc47a746e1aa810b320c60c19f512bf99e05d43566bd1b8cd6b157f4d22c2e4cc3057a8fb5efbb46342bfc895d91c'

    def test_sign_hex(self):
        res = self.client.put(f'/account/{account_addr}', data=json.dumps({"hexstr" : "0x49e299a55346"}), content_type='application/json')
        assert res.json == '0xe7796dabad3157107bd0edd53809ae476142fc7d7f764b5410338762b5cbe69062143dcd21383c31c64f89385f9e09ceb772b2d2aafc73dd047afda24eb616421b'

    def test_sign_a_transaction(self):
        transaction = { 
            "to": "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55",
            "value": 1000000000,
            "gasPrice": 234567897654321,
            "chainId": 1,
            "gas": 2000000,
            "nonce": 0,
        }
        res = self.client.put(f'/account/{account_addr}', data=json.dumps(transaction), content_type='application/json')
        assert res.json == '0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008026a0e4d0f31c4b8f1ede853f6d63c6694631f7ffc971d503d2b86985458175c74bc3a01c5b9d229af81852397cd194872a753923aa3444755b3e2cbc37b9eec7ba65e3'
