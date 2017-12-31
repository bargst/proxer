import gevent

from web3 import Web3, HTTPProvider, IPCProvider

from datetime import datetime, timedelta

from dispatcher import SingleProvider

class MostRecentBlockProvider(SingleProvider):

    def __init__(self, providers, *args, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.providers = providers
        self.invalid_providers = {}
        self.provider_blockNumber = 0
        self.monitoring = gevent.spawn(self.monitor)

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
