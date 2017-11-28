#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse
from datetime import datetime, timedelta

from web3 import Web3, HTTPProvider, IPCProvider

import gevent
import gevent.wsgi
import gevent.queue
from gevent import monkey; monkey.patch_socket()

from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.wsgi import WsgiServerTransport
from tinyrpc.server.gevent import RPCServerGreenlets
from tinyrpc.dispatch import RPCDispatcher

class ProxyDispatcher(RPCDispatcher):

    def __init__(self, providers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.providers = providers
        self.invalid_providers = {}
        self.provider = None
        self.provider_blockNumber = 0
        self.monitoring = gevent.spawn(self.monitor)

    def get_method(self, name):
        """ 
        Use provider to request the result of rpc method `name'
        """
        # Simple alias for provider method
        def provider_method(*args):
            request = self.provider.make_request(name, params=args)
            print(request)
            if 'result' in request:
                return request['result']
            elif 'error' in request:
                raise Exception(request['error'])

            return None

        try:
            # Check if method is defined in this dispatcher
            return super().get_method(name)
        except KeyError:
            # Fallback to forwarding method to provider
            return provider_method

        raise KeyError(name)

    def get_provider_status(self, provider):
        """ 
        Function used to return status of provider.
        Catch exception, such as timeout, as an invalid provider
        """
        w3 = Web3(provider)
        try:
            return (provider, w3.eth.blockNumber)
        except:
            return None

    def monitor(self):
        """
        Active loop used to check satus of the providers
        """
        while True:
            # Start background check of provider status
            checks = [gevent.spawn(self.get_provider_status, provider) for provider in self.providers]
            gevent.joinall(checks, timeout=2)

            # Check the returned provider status
            for check in checks:

                # Elect provider based on returned status
                if check.value:
                    provider, block_number = check.value
                    if block_number > self.provider_blockNumber:
                        self.provider = provider
                        self.provider_blockNumber = block_number

                # Exclude invalid provider
                elif provider in self.providers:
                    self.providers.remove(provider)
                    self.invalid_providers[datetime.now()] = provider

            # Activate provider again after a timeout
            timeouts = [ date for date in self.invalid_providers if datetime.now() - date > timedelta(seconds=30) ]
            for date in timeouts:
                self.providers.append(self.invalid_providers.pop(date))

            # Give some time to others ...
            gevent.sleep(2)


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
        
        self.providers = self.args.providers
        self.transport = WsgiServerTransport(queue_class=gevent.queue.Queue)
        self.wsgi_server = gevent.wsgi.WSGIServer(('127.0.0.1', self.args.port), self.transport.handle)
        self.dispatcher = ProxyDispatcher(self.providers)
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
