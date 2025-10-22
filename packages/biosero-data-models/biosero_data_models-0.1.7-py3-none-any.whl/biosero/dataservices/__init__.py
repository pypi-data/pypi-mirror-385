from .restclient import AccessioningClient, QueryClient, TransportationClient
__all__ = [
    'AccessioningClient', 
    'QueryClient', 
    'TransportationClient', 
    'TransportationRequest', 
    'TransportationRequestStatus'
]

def __getattr__(name):
    if name == 'AccessioningClient':
        from .accessioningclient import AccessioningClient
        return AccessioningClient
    elif name == 'QueryClient':
        from .queryclient import QueryClient
        return QueryClient
    elif name in ('TransportationClient', 'TransportationRequest', 'TransportationRequestStatus'):
        from .transportation_client import TransportationClient, TransportationRequest, TransportationRequestStatus
        return {
            'TransportationClient': TransportationClient,
            'TransportationRequest': TransportationRequest,
            'TransportationRequestStatus': TransportationRequestStatus
        }[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")
