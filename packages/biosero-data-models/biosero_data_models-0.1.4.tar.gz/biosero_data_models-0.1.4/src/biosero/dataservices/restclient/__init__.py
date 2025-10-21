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
    elif name == 'TransportationClient':
        from .transportation_client import TransportationClient
        return TransportationClient
    elif name == 'TransportationRequest':
        from .transportation_client import TransportationRequest
        return TransportationRequest
    elif name == 'TransportationRequestStatus':
        from .transportation_client import TransportationRequestStatus
        return TransportationRequestStatus
    raise AttributeError(f"module {__name__} has no attribute {name}")
