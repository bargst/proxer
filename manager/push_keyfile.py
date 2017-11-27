#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse
import json
import getpass

parser = argparse.ArgumentParser()
parser.add_argument("--manager", help="Account manager acces URL (default: http://localhost:5000/account/", metavar='http://host:port', type=str, default='http://localhost:5000/account/')
parser.add_argument("keyfile", help="Add keyfile to account manager", nargs='+')
args = parser.parse_args()

for keyfile in args.keyfile:
    with open(keyfile, 'r') as f:
        print("Add account to manager")
        r = requests.post(args.manager, json=json.load(f))
        address = r.json()
        if address:
            print('    {} added to manager, trying to unlock ...'.format(address))
            password = getpass.getpass()
            r = requests.post(args.manager + address, json={"password" : password})
            result = r.json()
            if 'locked' in result and not result['locked']:
                print("    {} unlocked".format(address))
                print('')
