#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent
import gevent.wsgi
import gevent.queue

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.wsgi import WsgiServerTransport
from tinyrpc.server.gevent import RPCServerGreenlets
from tinyrpc.dispatch import RPCDispatcher

from web3 import HTTPProvider
#provider = HTTPProvider('http://localhost:8545')
provider = HTTPProvider('https://mainnet.infura.io')

class ProxyDispatcher(RPCDispatcher):

    def get_method(self, name):

        def provider_method(*args):
            return provider.make_request(name, params=args)

        try:
            return super().get_method(name)
        except KeyError:
            return provider_method

        raise KeyError(name)

dispatcher = ProxyDispatcher()
transport = WsgiServerTransport(queue_class=gevent.queue.Queue)

# start wsgi server as a background-greenlet
wsgi_server = gevent.wsgi.WSGIServer(('127.0.0.1', 8545), transport.handle)
gevent.spawn(wsgi_server.serve_forever)

rpc_server = RPCServerGreenlets(
    transport,
    JSONRPCProtocol(),
    dispatcher
)

import requests
account_url = 'http://localhost:5000/account/'

@dispatcher.public
def eth_sign(addr, data):
    return requests.put(account_url + addr, json={'hexstr':data}).json()

@dispatcher.public
def eth_sendTransaction(transaction):
    addr = transaction.pop('from')
    #TODO check transaction content
    signed = requests.put(account_url + addr, json=transaction).json()
    return dispatcher.get_method('eth_sendRawTransaction')(signed)

# in the main greenlet, run our rpc_server
rpc_server.serve_forever()
