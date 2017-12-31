
class TestProxer:

    def test_todo(self):
        #TODO
        assert 0

        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--proxer-rpc", help="A remote HTTP-RPC ethereum node", metavar='http://host:port', type=str, default='http://localhost:8545')
        parser.add_argument("--remote-rpc", help="A remote HTTP-RPC ethereum node", metavar='http://host:port', type=str)
        parser.add_argument("--tinyrpc", help="Test using tinyrpc client", action='store_true', default=False)
        parser.add_argument("--no-web3", help="Test not using web3", action='store_true', default=False)
        parser.add_argument("--account", help="Use account to test signing")
        args = parser.parse_args()

        # web3 tests
        if not args.no_web3:
            from web3 import Web3, HTTPProvider, IPCProvider

            providers = { 'Proxer' : Web3(HTTPProvider(args.proxer_rpc)) }
            if args.remote_rpc:
                providers['Remote'] = Web3(HTTPProvider(args.remote_rpc))

            for provider in providers:
                print('{} eth_syncing: {}'.format(provider, providers[provider].eth.syncing))
                print('{} eth_blockNumber: {}'.format(provider, providers[provider].eth.blockNumber))
                print('{} eth_getCode: {}'.format(provider, providers[provider].eth.getCode('0xe819300B6f3d0625632B47196233fe6671a59891')))
                if args.account:
                    print('{} eth_sign: {}'.format(provider, providers[provider].eth.sign(args.account, text='test')))

        # tinyrpc tests
        if args.tinyrpc:
            from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
            from tinyrpc.transports.http import HttpPostClientTransport
            from tinyrpc import RPCClient

            # tinyrpc client setup
            rpc_client = RPCClient(
                JSONRPCProtocol(),
                HttpPostClientTransport(args.proxer_rpc)
            )
            remote_server = rpc_client.get_proxy()

            print('Proxer(tinyrpc) eth_syncing    : {}'.format(remote_server.eth_syncing()))
            print('Proxer(tinyrpc) eth_blockNumber: {}'.format(remote_server.eth_blockNumber()))

            if args.account:
                print(args.account)
                print('Proxer(tinyrpc) eth_sign: {}'.format(remote_server.eth_sign(args.account, '0x74657376')))
                transaction = {'from': args.account,
                               'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                               'value': 0,
                               'gas': 1,
                               'gasPrice': 1,
                               'nonce': 0,
                               'chainId': 1,
                               'data': '',
                               }
                print('Proxer(tinyrpc) eth_sendTransaction: {}'.format(remote_server.eth_sendTransaction(transaction)))
