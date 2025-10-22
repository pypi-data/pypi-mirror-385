

import configparser

from biosero.utilities.plate_data import PlateData
from biosero.datamodels.measurement import Volume, VolumeUnit
from biosero.utilities.liquid import Liquid

from biosero.dataservices.restclient.queryclient import QueryClient

config = configparser.ConfigParser()
config.read("config.ini")
url = "http://10.0.0.234:30081" #config["DATA SERVICES"]["url"]






qc = QueryClient(url)

my_id = qc.get_identity("RRRRRRR")








# Create a PlateData instance
plate_data = PlateData(url)


plate_data.register_plate_and_wells(barcode="777777", name="Test Plate", rows=2, columns=2)

# Register the plate and wells and update the location of the well identities to the plate
#plate_data.register_plate_and_wells(rows=2, columns=2)

# Get the Unique identifiers for the source and desination wells based on there location in the plate
source_well = plate_data.get_well_identifier(row=2, column=2)
dest_well = plate_data.get_well_identifier(row=2, column=1)

liquid = Liquid(url)

liquid.Transfer(source_identifier=source_well, destination_identifier=dest_well, volume=Volume(500, VolumeUnit.uL))



