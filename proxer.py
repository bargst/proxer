#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse

import gevent
import gevent.pywsgi
import gevent.queue
from gevent import monkey; monkey.patch_socket()

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.wsgi import WsgiServerTransport
from tinyrpc.server.gevent import RPCServerGreenlets

from web3 import HTTPProvider, IPCProvider

from dispatcher import SingleProvider, MostRecentBlockProvider

class Proxer:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--port", help="Listen localy on PORT (default: 8545)", default=8545, type=int)
        parser.add_argument("--ipc", help="Add IPC-RPC provider", action='append_const', dest='providers', const=IPCProvider())
        parser.add_argument("--local-rpc", help="Add HTTP-RPC provider: http://localhost:8545", action='append_const', dest='providers', const=HTTPProvider('http://localhost:8545'))
        parser.add_argument("--rpc", help="Add HTTP-RPC provider", metavar='http://host:port', action='append', dest='providers', type=HTTPProvider)
        parser.add_argument("--manager", help="Account manager acces URL", metavar='http://host:port', type=str)
        parser.add_argument("--debug", help="Enable debug output", dest='debug', action='store_true')
        parser.add_argument("--trace", help="Enable trace output", dest='trace', action='store_true')
        self.args = parser.parse_args()

        self.providers = self.args.providers if self.args.providers else [IPCProvider()]
        self.transport = WsgiServerTransport(queue_class=gevent.queue.Queue)
        self.wsgi_server = gevent.pywsgi.WSGIServer(('127.0.0.1', self.args.port), self.transport.handle)

        if len(self.providers) == 1:
            self.dispatcher = SingleProvider(self.providers[0])
        else:
            self.dispatcher = MostRecentBlockProvider(self.providers)

        self.rpc_server = RPCServerGreenlets(
            self.transport,
            JSONRPCProtocol(),
            self.dispatcher
        )

    def eth_sign(self, addr, data):
        return requests.put(self.args.manager + addr, json={'hexstr':data}).json()

    def eth_sendTransaction(self, tx):
        addr = tx.pop('from')
        #TODO check transaction content
        signed = requests.put(self.args.manager + addr, json=tx).json()
        #TODO check signed result
        return self.dispatcher.get_method('eth_sendRawTransaction')(signed)

    def start(self):

        if self.args.manager:
            self.dispatcher.add_method(self.eth_sign)
            self.dispatcher.add_method(self.eth_sendTransaction)

        # start wsgi server as a background-greenlet
        gevent.spawn(self.wsgi_server.serve_forever)

        # in the main greenlet, run our rpc_server
        self.rpc_server.serve_forever()


if __name__ == '__main__':
    Proxer().start()
