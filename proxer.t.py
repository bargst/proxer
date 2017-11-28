#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--rpc", help="A remote HTTP-RPC ethereum node", metavar='http://host:port', type=str, default='http://localhost:8545')
parser.add_argument("--remote-rpc", help="A remote HTTP-RPC ethereum node", metavar='http://host:port', type=str)
parser.add_argument("--tinyrpc", help="Test using tinyrpc client", action='store_true', default=False)
parser.add_argument("--no-web3", help="Test not using web3", action='store_true', default=False)
parser.add_argument("--account", help="Use account to test signing")
args = parser.parse_args()

if not args.no_web3:
    from web3 import Web3, HTTPProvider, IPCProvider

    proxer_web3 = Web3(HTTPProvider(args.rpc))
    print('Proxer eth_syncing: {}'.format(proxer_web3.eth.syncing))
    print('Proxer eth_blockNumber: {}'.format(proxer_web3.eth.blockNumber))
    if args.account:
        print(args.account)
        print('Proxer eth_sign: {}'.format(proxer_web3.eth.sign(args.account, text='test')))

    if args.remote_rpc:
        direct_web3 = Web3(HTTPProvider(args.remote_rpc))
        print('Direct eth_syncing: {}'.format(direct_web3.eth.syncing))
        print('Direct eth_blockNumber: {}'.format(direct_web3.eth.blockNumber))

        if args.account:
            print('Direct eth_sign: {}'.format(direct_web3.eth.sign(args.account, text='test')))

# tinyrpc tests
if args.tinyrpc:
    from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
    from tinyrpc.transports.http import HttpPostClientTransport
    from tinyrpc import RPCClient

    # tinyrpc client setup
    rpc_client = RPCClient(
        JSONRPCProtocol(),
        HttpPostClientTransport(args.rpc)
    )
    remote_server = rpc_client.get_proxy()

    print('eth_blockNumber: {}'.format(remote_server.eth_blockNumber()))
    print('eth_syncing    : {}'.format(remote_server.eth_syncing()))

    if args.account:
        print(args.account)
        print('eth_sign: {}'.format(remote_server.eth_sign(args.account, '0x74657376')))
        transaction = {'from': args.account,
                       'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                       'value': 0,
                       'gas': 1,
                       'gasPrice': 1,
                       'nonce': 0,
                       'chainId': 1,
                       'data': '',
                       }
        print('eth_sendTransaction: {}'.format(remote_server.eth_sendTransaction(transaction)))
