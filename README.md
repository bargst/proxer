# proxer

A Simple ethereum proxy with a manager for local transaction signing.

## Setup

This project use pipenv to install required dependencies. See https://docs.pipenv.org/.

### Proxer
```
pipenv --three
pipenv install
pipenv run ./proxer.py --help
```

## Example Usage

```
pipenv run ./proxer.py --manager http://localhost:5000/account/ --local-rpc --rpc http://192.168.1.42:8545 --rpc https://mainnet.infura.io --api
```

This example lauch an Ethereum RPC Proxy listening on localhost:8545 and forwarding requests to :
* http://localhost:8545
* http://192.168.1.42:8545
* https://mainnet.infura.io

The server also listen to port 5000 for rest request, like account API : 
```
# Populate with standard account keyfile:
pipenv run python manager/push_keyfile.py $HOME/.ethereum/keystore/*
```

## Testing

TODO, see tests/ directory.
