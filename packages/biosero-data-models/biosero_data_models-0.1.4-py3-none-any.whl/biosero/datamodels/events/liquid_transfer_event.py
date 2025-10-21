from dataclasses import dataclass, asdict
from datetime import datetime
from biosero.datamodels.measurement import Volume
from typing import Optional

@dataclass
class LiquidTransferEvent:
    SourceIdentifier: str
    DestinationIdentifier: str
    ActualTransferVolume: Volume
    TimeStamp: datetime

    TransferError: Optional[bool] = False
    TransferErrorDescription: Optional[str] = None

    TransferType: Optional[str] = None 
    IntendedTransferVolume: Optional[Volume] = None
    TransferDeviceIdentifier: Optional[str] = None
    PipetteMandrelIdentifier: Optional[str] = None  # what mandrel was used on the pipette
    PipetteTipTypeIdentifier: Optional[str] = None  # what kind of tip
    PipetteTipLocationInBox: Optional[str] = None  # where was it located in the box
    PipetteTipBoxIdentifier: Optional[str] = None  # what box or lot number
    OperatorIdentifier: Optional[str] = None  # who did the transfer if manual, who setup the run if automatic
    PipetteTechnique: Optional[str] = None  # can be used to specify additional information about how the transfer was made, speed, offset, follow liquid, etc.
    LiquidTypeSpecified: Optional[str] = None  # liquid type defined for the dispenser
    LiquidTypeCalibrationUsed: Optional[str] = None  # liquid calibration used by the dispenser
    TransferErrorDescription: Optional[str] = None
    DropSize: Optional[Volume] = None  # if multiple drops/dispenses used (ex: acoustic dispenser) then dropsize used.


    ClassName: str = "Biosero.DataModels.Events.LiquidTransferEvent"

    def __post_init__(self):
        # Validate ActualTransferVolume
        if not isinstance(self.ActualTransferVolume, Volume):
            raise TypeError(f"ActualTransferVolume must be an instance of Volume, got {type(self.ActualTransferVolume)}")
        
        # Validate TimeStamp
        if not isinstance(self.TimeStamp, datetime):
            raise TypeError(f"TimeStamp must be an instance of datetime, got {type(self.TimeStamp)}")


    def to_dict(self):
        data = asdict(self)
        data["IntendedTransferVolume"] = self.IntendedTransferVolume.to_dict() if isinstance(self.IntendedTransferVolume, Volume) else self.IntendedTransferVolume
        data["ActualTransferVolume"] = self.ActualTransferVolume.to_dict() if isinstance(self.ActualTransferVolume, Volume) else self.ActualTransferVolume
        data["DropSize"] = self.DropSize.to_dict() if isinstance(self.DropSize, Volume) else self.DropSize
        if isinstance(self.TimeStamp, datetime):
            data["TimeStamp"] = self.TimeStamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return data

    def __str__(self):
        return (f"LiquidTransferEvent("
                f"SourceIdentifier={self.SourceIdentifier}, "
                f"DestinationIdentifier={self.DestinationIdentifier}, "
                f"IntendedTransferVolume={self.IntendedTransferVolume}, "
                f"ActualTransferVolume={self.ActualTransferVolume}, "
                f"TransferError={self.TransferError}, "
                f"TransferErrorDescription={self.TransferErrorDescription}, "
                f"TimeStamp={self.TimeStamp}, "
                f"TransferType={self.TransferType}, "
                f"TransferDeviceIdentifier={self.TransferDeviceIdentifier}, "
                f"PipetteMandrelIdentifier={self.PipetteMandrelIdentifier}, "
                f"PipetteTipTypeIdentifier={self.PipetteTipTypeIdentifier}, "
                f"PipetteTipLocationInBox={self.PipetteTipLocationInBox}, "
                f"PipetteTipBoxIdentifier={self.PipetteTipBoxIdentifier}, "
                f"OperatorIdentifier={self.OperatorIdentifier}, "
                f"PipetteTechnique={self.PipetteTechnique}, "
                f"LiquidTypeSpecified={self.LiquidTypeSpecified}, "
                f"LiquidTypeCalibrationUsed={self.LiquidTypeCalibrationUsed}, "
                f"DropSize={self.DropSize})")
