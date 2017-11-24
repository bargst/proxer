#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse

from web3 import HTTPProvider, IPCProvider

import gevent
import gevent.wsgi
import gevent.queue

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.wsgi import WsgiServerTransport
from tinyrpc.server.gevent import RPCServerGreenlets
from tinyrpc.dispatch import RPCDispatcher

class ProxyDispatcher(RPCDispatcher):

    def __init__(self, providers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.providers = providers

    def get_method(self, name):

        print(self.providers)
        def provider_method(*args):
            for provider in self.providers:
                return provider.make_request(name, params=args)

        try:
            return super().get_method(name)
        except KeyError:
            return provider_method

        raise KeyError(name)


class Proxer:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ipc", help="Add IPC-RPC provider", action='append_const', dest='providers', const=IPCProvider())
        parser.add_argument("--local-rpc", help="Add HTTP-RPC provider: http://localhost:8545", action='append_const', dest='providers', const=HTTPProvider('http://localhost:8545'))
        parser.add_argument("--rpc", help="Add HTTP-RPC provider", metavar='http://host:port', action='append', dest='providers', type=HTTPProvider)
        parser.add_argument("--manager", help="Account manager acces URL", metavar='http://host:port', type=str)
        parser.add_argument("--debug", help="Enable debug output", dest='debug', action='store_true')
        parser.add_argument("--trace", help="Enable trace output", dest='trace', action='store_true')
        self.args = parser.parse_args()
        
        self.providers = self.args.providers
        self.transport = WsgiServerTransport(queue_class=gevent.queue.Queue)
        self.wsgi_server = gevent.wsgi.WSGIServer(('127.0.0.1', 8545), self.transport.handle)
        self.dispatcher = ProxyDispatcher(self.providers)
        self.rpc_server = RPCServerGreenlets(
            self.transport,
            JSONRPCProtocol(),
            self.dispatcher
        )


    def start(self):
        # start wsgi server as a background-greenlet
        gevent.spawn(self.wsgi_server.serve_forever)
        
        # in the main greenlet, run our rpc_server
        self.rpc_server.serve_forever()

#account_url = 'http://localhost:5000/account/'
#account_url = self.args.account_manager

#    @dispatcher.public
#    def eth_sign(addr, data):
#        return requests.put(account_url + addr, json={'hexstr':data}).json()

#    @dispatcher.public
#    def eth_sendTransaction(transaction):
#        addr = transaction.pop('from')
#        #TODO check transaction content
#        signed = requests.put(account_url + addr, json=transaction).json()
#        return dispatcher.get_method('eth_sendRawTransaction')(signed)


if __name__ == '__main__':
    Proxer().start()
