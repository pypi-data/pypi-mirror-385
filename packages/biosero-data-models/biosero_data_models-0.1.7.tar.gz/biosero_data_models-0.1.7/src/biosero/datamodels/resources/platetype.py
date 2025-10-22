from .identity import Identity

class PlateType(Identity):
    def __init__(self):
        super().__init__()
        self.Manufacturer = None
        self.CommonName = None
        self.PartNumber = None
        self.WellWorkingVolume = None
        self.Rows = None
        self.Columns = None
        self.ImageUrl = None

    @property
    def Wells(self):
        return self.Rows * self.Columns if self.Rows and self.Columns else None