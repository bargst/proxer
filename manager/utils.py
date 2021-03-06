import os
import json
import pkg_resources
from web3 import Web3

env_web3 = os.environ.get('WEB3_PROVIDER_URI', '')
if env_web3.startswith('rest+'):
    from web3_restprovider import RESTProvider
    web3 = Web3(RESTProvider(env_web3[len('rest+'):]))
else:
    web3 = Web3()

token_addresses =  {
    'OWETH': '0xECF8F87f810EcF450940c9f60066b4a7a501d6A7',
    'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    'DAI': '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359',
    'SAI': '0x59aDCF176ED2f6788A41B8eA4c4904518e62B6A4',
    'MKR': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
    'DGD': '0xE0B7927c4aF23765Cb51314A0E0521A9645F0E2A',
    'W-GNT': '0x01AfC37F4F85babc47c0E2d0EAbABC7FB49793c8',
    'REP': '0xE94327D07Fc17907b4DB788E5aDf2ed424adDff6',
    'ICN': '0x888666CA69E0f178DED6D75b5726Cee99A87D698',
    '1ST': '0xAf30D2a7E90d7DC361c8C4585e9BB7D2F6f15bc7',
    'SNGLS': '0xaeC2E87E0A235266D9C5ADc9DEb4b2E29b54D009',
    'VSL': '0x5c543e7AE0A1104f78406C340E9C64FD9fCE5170',
    'PLU': '0xD8912C10681D8B21Fd3742244f44658dBA12264E',
    'MLN': '0xBEB9eF514a379B997e0798FDcC901Ee474B6D9A1',
    'RHOC': '0x168296bb09e24A88805CB9c33356536B980D3fC5',
    'TIME': '0x6531f133e6DeeBe7F2dcE5A0441aA7ef330B4e53',
    'GUP': '0xf7B098298f7C69Fc14610bf71d5e02c60792894C',
    'BAT': '0x0D8775F648430679A709E98d2b0Cb6250d2887EF',
    'NMR': '0x1776e1F26f98b1A5dF9cD347953a26dd3Cb46671'
}

def load_abi(package, resource):
    return json.loads(pkg_resources.resource_string(package, resource))

ERC20Token = web3.eth.contract(abi=load_abi('pymaker', 'abi/ERC20Token.abi'))
DSEthToken = web3.eth.contract(abi=load_abi('pymaker', 'abi/DSEthToken.abi'))
tokens = { name: ERC20Token(address=token_addresses[name]) for name in token_addresses }
tokens['OWETH'] = DSEthToken(address=token_addresses['OWETH'])
tokens['WETH'] = DSEthToken(address=token_addresses['WETH'])

def cast_addr(string):
    try:
        address = Web3.toChecksumAddress(string)
    except:
        address = None

    return address
