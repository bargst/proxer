#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent.wsgi import WSGIServer
from account import app

http_server = WSGIServer(('127.0.0.1', 5000), app)
http_server.serve_forever()
