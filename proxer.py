#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent
from gevent import monkey ; monkey.patch_all()
import gevent.pywsgi
import gevent.queue

import requests
import argparse

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.wsgi import WsgiServerTransport
from tinyrpc.server.gevent import RPCServerGreenlets

from werkzeug.wsgi import DispatcherMiddleware

from web3 import Web3, HTTPProvider, IPCProvider

from manager import manager_app
from markets import markets_app, OasisMarket

from dispatcher import SingleProvider, MostRecentBlockProvider

class Proxer:
    def __init__(self):
        parser = argparse.ArgumentParser()
        # Proxy options
        parser.add_argument("--no-proxy", help="Do not start local rpc proxy", action='store_true')
        parser.add_argument("--host", help="Listen on host IP (default: 127.0.0.1)", default='127.0.0.1')
        parser.add_argument("--port", help="Listen localy on PORT (default: 8545)", default=8545, type=int)
        parser.add_argument("--ipc", help="Add IPC-RPC provider to proxy", action='append_const', dest='providers', const=IPCProvider())
        parser.add_argument("--local-rpc", help="Add http://localhost:8545 provider to proxy", action='append_const', dest='providers', const=HTTPProvider('http://localhost:8545'))
        parser.add_argument("--rpc", help="Add HTTP-RPC provider to proxy", metavar='http://host:port', action='append', dest='providers', type=HTTPProvider)
        # API options
        parser.add_argument("--api", help="Start the rest API", action='store_true')
        parser.add_argument("--api-host", help="API host IP to listen to (default: 127.0.0.1)", default='127.0.0.1')
        parser.add_argument("--api-port", help="API port to listen localy (default: 5000)", default=5000, type=int)
        parser.add_argument("--manager-url", help="Account manager acces URL", metavar='http://host:port', type=str)

        parser.add_argument("--debug", help="Enable debug output", dest='debug', action='store_true')
        parser.add_argument("--trace", help="Enable trace output", dest='trace', action='store_true')
        self.args = parser.parse_args()


        # Greenlets
        self.greenlets = []

        # Create a dispatcher depending on number of providers
        self.providers = self.args.providers if self.args.providers else [IPCProvider()]
        if len(self.providers) == 1:
            self.dispatcher = SingleProvider(self.providers[0])
        else:
            self.dispatcher = MostRecentBlockProvider(self.providers)

        if self.args.manager_url:
            self.dispatcher.add_method(self.eth_sign)
            self.dispatcher.add_method(self.eth_sendTransaction)

        # Web3 provider
        self.web3 = Web3(self.providers)


        if not self.args.no_proxy:
            # TinyRPC WSGI Server
            self.transport = WsgiServerTransport(queue_class=gevent.queue.Queue)
            self.wsgi_server = gevent.pywsgi.WSGIServer((self.args.host, self.args.port), self.transport.handle)
            self.greenlets.append(self.wsgi_server.serve_forever)

            # TinyRPC RPC Server
            self.rpc_server = RPCServerGreenlets(
                self.transport,
                JSONRPCProtocol(),
                self.dispatcher
            )
            self.greenlets.append(self.rpc_server.serve_forever)

        # Rest API server
        if self.args.api:
            markets_app.extensions['oasis_market'] = OasisMarket(self.web3)
            self.api_application = DispatcherMiddleware(manager_app, { '/market': markets_app })

            self.api_server = gevent.pywsgi.WSGIServer((self.args.api_host, self.args.api_port), self.api_application)
            self.greenlets.append(self.api_server.serve_forever)

    def eth_sign(self, addr, data):
        return requests.put(self.args.manager + addr, json={'hexstr':data}).json()

    def eth_sendTransaction(self, tx):
        addr = tx.pop('from')
        #TODO check transaction content
        signed = requests.put(self.args.manager + addr, json=tx).json()
        #TODO check signed result
        return self.dispatcher.get_method('eth_sendRawTransaction')(signed)

    def start(self):
        # Spawn and wait for the greenlets to finish.
        gevent.joinall([gevent.spawn(greenlet) for greenlet in self.greenlets])

if __name__ == '__main__':
    Proxer().start()
