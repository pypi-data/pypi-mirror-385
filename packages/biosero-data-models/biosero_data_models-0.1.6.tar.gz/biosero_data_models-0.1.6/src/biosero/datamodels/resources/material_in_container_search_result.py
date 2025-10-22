from biosero.datamodels.measurement import Concentration, Volume, Weight

class MaterialInContainerSearchResult:
    def __init__(self, containerIdentifier, materialIdentifier, concentration, netVolume, netWeight, path):
        self.containerIdentifier = containerIdentifier
        self.materialIdentifier = materialIdentifier
        self.concentration = Concentration(**concentration)
        self.netVolume = Volume(**netVolume)
        self.netWeight = Weight(**netWeight)
        self.path = path

    @classmethod
    def from_dict(cls, data):
        return cls(
            containerIdentifier=data.get('containerIdentifier'),
            materialIdentifier=data.get('materialIdentifier'),
            concentration=data.get('concentration'),
            netVolume=data.get('netVolume'),
            net_weight=data.get('netWeight'),
            path=data.get('path')
        )
