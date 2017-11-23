#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.http import HttpPostClientTransport
from tinyrpc import RPCClient

rpc_client = RPCClient(
    JSONRPCProtocol(),
    HttpPostClientTransport('http://127.0.0.1:8545/')
)

remote_server = rpc_client.get_proxy()

account_url = 'http://localhost:5000/account/'
accounts = requests.get(account_url).json()
addr = accounts[0]

#result = remote_server.eth_blockNumber()
result = remote_server.eth_call({'to': '0xe819300b6f3d0625632b47196233fe6671a59891', 'from': addr, 'data': '0xbe38a4fe'}, 'latest')
#result = remote_server.eth_getCode(addr, 'latest')
#result = remote_server.eth_doesnotexist(addr, 'latest')
#result = remote_server.eth_sign(addr, '0x74657374')
{
                                                            }
transaction = { 'from': addr,
                'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                'value': 1000000000,

                'gas': 2000000,
                'gasPrice': 234567897654321,
                'nonce': 0,
                'chainId': 1,
                'data': '',
}
#result = remote_server.eth_sendTransaction(transaction)
print('Server answered: ', result)
