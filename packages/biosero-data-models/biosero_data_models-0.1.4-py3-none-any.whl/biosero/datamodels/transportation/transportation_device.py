class TransportationDevice:
    def __init__(self, identifier: str, internalStations: list, externalAccessibleStations: list):
        self.identifier = identifier
        self.internalStations = internalStations
        self.externalAccessibleStations = externalAccessibleStations

    def assign(self, request):
        raise NotImplementedError("This method needs to be implemented by subclasses")
