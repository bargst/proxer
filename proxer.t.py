#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.http import HttpPostClientTransport
from tinyrpc import RPCClient

rpc_client = RPCClient(
    JSONRPCProtocol(),
    HttpPostClientTransport('http://127.0.0.1:8545/')
    #HttpPostClientTransport('http://192.168.1.7:8545/')
)

remote_server = rpc_client.get_proxy()

print('eth_blockNumber: {}'.format(remote_server.eth_blockNumber()))
print('eth_syncing    : {}'.format(remote_server.eth_syncing()))

account_url = 'http://localhost:5000/account/'
try:
    accounts = requests.get(account_url).json()
    addr = accounts[0]
except:
    addr = None

if addr:
    print(addr)
    print('eth_sign: {}'.format(remote_server.eth_sign(addr, '0x74657376')))
    transaction = { 'from': addr,
                    'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                    'value': 1,

                    'gas': 1,
                    'gasPrice': 1,
                    'nonce': 0,
                    'chainId': 1,
                    'data': '',
    }
    print('eth_sendTransaction: {}'.format(remote_server.eth_sendTransaction(transaction)))
