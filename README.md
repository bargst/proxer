# proxer

A Simple ethereum proxy with a manager for local transaction signing.

## Setup

This project use pipenv to install required dependencies. See https://docs.pipenv.org/.

### Proxer
```
pipenv install
pipenv run ./proxer.py --help
```

### Manager (optional)

Run the manager daemon :
```
pipenv run manager/manager.py
```

Populate with standard account keyfile:
```
pipenv run python manager/push_keyfile.py $HOME/.ethereum/keystore/*
```

## Example Usage

```
pipenv run ./proxer.py --manager http://localhost:5000/account/ --local-rpc --rpc http://192.168.1.42:8545 --rpc https://mainnet.infura.io
```

This example lauch an Ethereum RPC Proxy listening on localhost:8545 and forwarding requests to :
* http://localhost:8545
* http://192.168.1.42:8545
* https://mainnet.infura.io

With the exception of signing request handled by the manager at http://localhost:5000/account/.

## Testing
```
pipenv run ./proxer.t.py
pipenv run python manager/account.t.py
```

