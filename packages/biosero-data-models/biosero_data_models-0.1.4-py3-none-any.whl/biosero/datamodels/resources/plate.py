from .platetype import PlateType

class Plate(PlateType):
    def __init__(self, plateType=None):
        if plateType is None:
            super().__init__()
        else:
            self.Properties = plateType.Properties.copy()
            self.Identifier = ''
            self.TypeIdentifier = plateType.Identifier
            self.Description = plateType.Description
            self.IsInstance = True