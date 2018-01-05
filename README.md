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

### API
Some available APIs
```
curl http://localhost:5000/markets/oasis/book/WETH/DAI
curl http://localhost:5000/markets/daiv1
{
  "cap": 50000000.0,
  "chi": 1.0,
  "din": 1877069.75,
  "gap": 1.0,
  "mat": 1.5,
  "per": 1.0000019693612086,
  "tag": 831.7746380614806,
  "tax": 1.0
}
curl http://localhost:5000/markets/daiv1/cups
curl http://localhost:5000/markets/daiv1/cups/42
{
  "art": 1000.0,
  "id": 42,
  "ink": 3.0,
  "lad": "0xfa7c0b7331d0F43ae6f9ebE02Ac336c8986a7014",
  "safe": true
}
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

```
pipenv install --dev
make test
```
