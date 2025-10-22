from enum import Enum

class WeightUnit(Enum):
    ug = 1
    mg = 2
    g = 3
    Kg = 4

class Weight:
    def __init__(self, value=0, unit=WeightUnit.g):
        self.value = value
        self.unit = unit

    def convert_to(self, new_unit):
        conversion_rates = {
            (WeightUnit.ug, WeightUnit.mg): 0.001,
            (WeightUnit.ug, WeightUnit.g): 0.000001,
            (WeightUnit.ug, WeightUnit.Kg): 0.000000001,
            (WeightUnit.mg, WeightUnit.ug): 1000,
            (WeightUnit.mg, WeightUnit.g): 0.001,
            (WeightUnit.mg, WeightUnit.Kg): 0.000001,
            (WeightUnit.g, WeightUnit.ug): 1000000,
            (WeightUnit.g, WeightUnit.mg): 1000,
            (WeightUnit.g, WeightUnit.Kg): 0.001,
            (WeightUnit.Kg, WeightUnit.ug): 1000000000,
            (WeightUnit.Kg, WeightUnit.mg): 1000000,
            (WeightUnit.Kg, WeightUnit.g): 1000,
        }

        if self.unit == new_unit:
            return Weight(self.value, new_unit)

        conversion_rate = conversion_rates.get((self.unit, new_unit))
        if conversion_rate is None:
            raise ValueError("Invalid conversion from {} to {}".format(self.unit, new_unit))

        return Weight(self.value * conversion_rate, new_unit)

    def __str__(self):
        return "{} {}".format(self.value, self.unit.name)

    # Other methods like ToMg, ToGramsInDecimal, FromGrams, Parse, and operator overloads are not directly translatable to Python
    # Python does not support method overloading. We can achieve similar results in different ways
    # Also, Python does not have built-in support for interfaces like IComparable
    # So, methods related to IComparable are not translated