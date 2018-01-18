#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gevent
from gevent import monkey ; monkey.patch_all()
import gevent.pywsgi

import argparse

from werkzeug.wsgi import DispatcherMiddleware

from web3 import Web3, HTTPProvider, IPCProvider

from manager import manager_app
from markets import app_push_web3, markets_app, OasisMarket


class Proxer:
    def __init__(self):
        parser = argparse.ArgumentParser()
        # Proxy options
        parser.add_argument("--ipc", help="Add IPC-RPC provider to proxy", action='append_const', dest='providers', const=IPCProvider())
        parser.add_argument("--local-rpc", help="Add http://localhost:8545 provider to proxy", action='append_const', dest='providers', const=HTTPProvider('http://localhost:8545'))
        parser.add_argument("--rpc", help="Add HTTP-RPC provider to proxy", metavar='http://host:port', action='append', dest='providers', type=HTTPProvider)
        parser.add_argument("--rest", help="Add REST provider to proxy", metavar='http://host:port/path')
        # API options
        parser.add_argument("--host", help="Host IP to listen to (default: 127.0.0.1)", default='127.0.0.1')
        parser.add_argument("--port", help="Port to listen to (default: 5000)", default=5000, type=int)
        parser.add_argument("--manager-url", help="Account manager acces URL", metavar='http://host:port', type=str)

        parser.add_argument("--debug", help="Enable debug output", dest='debug', action='store_true')
        parser.add_argument("--trace", help="Enable trace output", dest='trace', action='store_true')
        self.args = parser.parse_args()

        # Greenlets
        self.greenlets = []

        self.providers = self.args.providers  if self.args.providers else []

        # Web3 RESTProvider
        if self.args.rest:
            from web3_restprovider import RESTProvider
            self.providers.append(RESTProvider(self.args.rest))

        env_web3 = os.environ.get('WEB3_PROVIDER_URI', '')
        if env_web3.startswith('rest+'):
            from web3_restprovider import RESTProvider
            self.providers.append(RESTProvider(env_web3[len('rest+'):]))

        # Web3 provider
        self.web3 = Web3(self.providers) if self.providers else Web3()

        app_push_web3(markets_app, self.web3)
        self.application = DispatcherMiddleware(manager_app, { '/markets': markets_app })

        self.server = gevent.pywsgi.WSGIServer((self.args.host, self.args.port), self.application)
        self.greenlets.append(self.server.serve_forever)

    def start(self):
        # Spawn and wait for the greenlets to finish.
        gevent.joinall([gevent.spawn(greenlet) for greenlet in self.greenlets])

if __name__ == '__main__':
    Proxer().start()
