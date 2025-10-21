from biosero.datamodels.measurement import Concentration, Volume, Weight

class SampleInContainerSearchResult:
    def __init__(self, container_identifier, sample_identifier, concentration, net_volume, net_weight, path):
        self.container_identifier = container_identifier
        self.sample_identifier = sample_identifier
        self.concentration = Concentration(**concentration)
        self.net_volume = Volume(**net_volume)
        self.net_weight = Weight(**net_weight)
        self.path = path

    @classmethod
    def from_dict(cls, data):
        return cls(
            container_identifier=data.get('ContainerIdentifier'),
            sample_identifier=data.get('SampleIdentifier'),
            concentration=data.get('Concentration'),
            net_volume=data.get('NetVolume'),
            net_weight=data.get('NetWeight'),
            path=data.get('Path')
        )
