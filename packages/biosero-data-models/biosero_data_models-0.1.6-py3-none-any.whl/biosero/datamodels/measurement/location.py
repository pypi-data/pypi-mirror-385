from dataclasses import field, dataclass

# @dataclass
# class Location():
#     ParentIdentifier: str = field(default=None)
#     ItemIdentifier: str = field(default=None)
#     Coordinates: any = field(default=None)

#     def to_dict(self):
#         return {
#             "ParentIdentifier": self.ParentIdentifier,
#             "ItemIdentifier": self.ItemIdentifier,
#             "Coordinates": self.Coordinates
#         }

@dataclass
class Location():
    parentIdentifier: str = field(default=None)
    itemIdentifier: str = field(default=None)
    coordinates: any = field(default=None)

    def to_dict(self):
        return {
            "parentIdentifier": self.parentIdentifier,
            "itemIdentifier": self.itemIdentifier,
            "coordinates": self.coordinates
        }
