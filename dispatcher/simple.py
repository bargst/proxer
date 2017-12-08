from tinyrpc.dispatch import RPCDispatcher

class SingleProvider(RPCDispatcher):

    def __init__(self, provider, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = provider

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
