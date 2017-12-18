import requests
account_url = 'http://localhost:5000/account/'
account_keyfile = {"address":"af63264ff89aa82b4d325477dbeedce3cf827552","crypto":{"cipher":"aes-128-ctr","ciphertext":"da9cb944aeb626fe4e353eb6f392984c7d81f98b6c971ce5c6f192b9425afcef","cipherparams":{"iv":"7a7a41fa41b1c2c2cdb8193fefa1a4d0"},"kdf":"scrypt","kdfparams":{"dklen":32,"n":262144,"p":1,"r":8,"salt":"dd12ffb0ee62ec4ed304572e308854c22c907a10cf5ad75a799d7dac7b57ba38"},"mac":"9815484fd13890521567f8aa069a668da1df102c11483d7847f9ed6ca30a9b84"},"id":"9cf8212a-0c6d-4770-a1c0-54e67b964d58","version":3}

class TestAccount:

    def test_accoun_manager(self):
        print("Add account to manager")
        r = requests.post(account_url, json=account_keyfile)
        address = r.json()
        print(address)

        print("Show accounts in manager")
        r = requests.get(account_url)
        print(r.json())

        print("Show account detail")
        r = requests.get(account_url + address)
        print(r.json())

        print("Unlock account with invalid password")
        r = requests.post(account_url + address, json={"password" : "invalid_password"})
        print(r.json())

        print("Unlock account with valid password")
        r = requests.post(account_url + address, json={"password" : "default"})
        print(r.json())

        print("Sign a text message")
        message = { 
            "text": "test",
        }
        r = requests.put(account_url + address, json=message)
        print(r.json())

        print("Sign a hex message")
        message = { 
            "hexstr": "0x49e299a55346",
        }
        r = requests.put(account_url + address, json=message)
        print(r.json())

        print("Sign a transaction")
        transaction = { 
            "to": "0xF0109fC8DF283027b6285cc889F5aA624EaC1F55",
            "value": 1000000000,
            "gasPrice": 234567897654321,
            "chainId": 1,
            "gas": 2000000,
            "nonce": 0,
        }
        r = requests.put(account_url + address, json=transaction)
        print(r.json())
