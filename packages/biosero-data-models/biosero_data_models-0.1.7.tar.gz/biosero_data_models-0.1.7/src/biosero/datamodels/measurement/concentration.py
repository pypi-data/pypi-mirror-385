from enum import Enum
import re

class ConcentrationUnit(Enum):
    mM = 1
    uM = 2
    nM = 3
    mgmL = 4

class Concentration:
    def __init__(self, value=None, unit=None):
        self.Value = value
        self.Unit = unit

    def calculate_molarity(self, molecular_weight):
        if self.Unit != ConcentrationUnit.mgmL:
            return self
        return Concentration((self.Value / molecular_weight) * 1000, ConcentrationUnit.mM)

    def to_micro_moles(self):
        if self.Unit == ConcentrationUnit.mM:
            return Concentration(self.Value * 1000, ConcentrationUnit.uM)
        elif self.Unit == ConcentrationUnit.nM:
            return Concentration(self.Value / 1000, ConcentrationUnit.uM)
        else:
            raise Exception(f"Conversion from {self.Unit} to uM is not supported")

    @staticmethod
    def parse(value):
        number = float(re.findall(r'[0-9.]+', value)[0])
        dimension = re.findall(r'[a-zA-Z]+', value)[0]
        return Concentration(number, ConcentrationUnit[dimension])

    def __str__(self):
        return f"{self.Value} {self.Unit.name}"

    def __eq__(self, other):
        if isinstance(other, Concentration):
            return self.to_micro_moles().Value == other.to_micro_moles().Value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.to_micro_moles().Value < other.to_micro_moles().Value

    def __le__(self, other):
        return self.to_micro_moles().Value <= other.to_micro_moles().Value

    def __gt__(self, other):
        return self.to_micro_moles().Value > other.to_micro_moles().Value

    def __ge__(self, other):
        return self.to_micro_moles().Value >= other.to_micro_moles().Value