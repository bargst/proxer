# proxer

A Simple ethereum proxy with a manager for local transaction signing.

## Setup 
```
pipenv install
pipenv run ./proxer.py &
```

## Test
```
pipenv run ./proxer.t.py
```

## Manager

Run the manager daemon : 
```
cd manager 
pipenv run ./account.sh &
```

Populate with a default account :
```
pipenv run python ./account.t.py
```

Test signing a message with Ethereum HTTP RPC `eth_sign`
