from enum import Enum

class Categories():

    class Schedulers(Enum):
        CELLARIO = 'Cellario'
        GENERA = 'Genera'
        MOMENTUM = 'Momentum'
        VWORKS = 'VWorks'

    class LIMS(Enum):
        LABWARE = 'Labware'
        LABVANTAGE = 'LabVantage'
        DOTMATICS = 'Dotmatics'
        MOSAIC = 'Mosaic'

    class ELN(Enum):
        BENCHLING = 'Benchling'
        SIGNALS = 'Signals'
    
    class LIQUID_HANDLING(Enum):
        FLUENT_CONTROL = 'Fluent Control'
        VENUS = 'Venus'
