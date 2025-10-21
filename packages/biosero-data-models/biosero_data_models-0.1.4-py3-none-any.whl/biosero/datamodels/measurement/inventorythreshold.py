from enum import Enum

class InventoryTriggerType(Enum):
    Restock = 1
    Reorder = 2

class InventoryThreshold:
    def __init__(self):
        self.Identifier = None
        self.ItemTypeId = None
        self.InventoryLocationId = None
        self.ThresholdLevel = None
        self.ThreasholdReachedWhenLevelIs = None
        self.Notes = None
        self.TriggeredOrderId = None
        self.TriggerType = None
        self.IsEnabled = None
        self.ReasonIfDisabled = None