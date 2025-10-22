from enum import Enum
import math

class VolumeUnit(Enum):
    L = 0
    mL = 3
    uL = 6
    nL = 9
    pL = 12
    fL = 15

class Volume:
    def __init__(self, amount=0, unit=VolumeUnit.L):
        self.amount = amount
        self.unit = unit

    def convert_to(self, unit):
        old_unit = self.unit.value
        new_unit = unit.value

        if old_unit == new_unit:
            return self

        power = new_unit - old_unit
        new_amount = self.amount * math.pow(10, power)

        return Volume(new_amount, unit)

    def to_liters(self):
        if self.unit == VolumeUnit.L:
            return self
        else:
            return Volume(self.convert_to(VolumeUnit.L).amount, VolumeUnit.L)

    def to_nanoliters(self):
        if self.unit == VolumeUnit.nL:
            return self
        else:
            return Volume(self.convert_to(VolumeUnit.nL).amount, VolumeUnit.nL)

    def to_liters_in_decimal(self):
        return self.to_liters().amount

    @staticmethod
    def from_liters(liters):
        return Volume(liters, VolumeUnit.L)
    
    def to_dict(self):
        return {
            "amount": self.amount,
            "unit": self.unit.name
        }

    # Overloading operators and other methods are not directly translatable to Python
    # Python does not support method overloading. We can achieve similar results in different ways
    # Also, Python does not have built-in support for interfaces like IComparable
    # So, methods related to IComparable are not translated