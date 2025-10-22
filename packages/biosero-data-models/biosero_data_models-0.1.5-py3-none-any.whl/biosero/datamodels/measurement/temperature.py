from enum import Enum

class TemperatureUnit(Enum):
    C = 1
    F = 2
    K = 3

class Temperature:
    def __init__(self, value=0.0, unit=TemperatureUnit.C):
        self.Value = value
        self.Unit = unit

    def ConvertTo(self, unit):
        if self.Unit == unit:
            return self
        elif unit == TemperatureUnit.C:
            return self.ToCelsius()
        elif unit == TemperatureUnit.F:
            return self.ToFahrenheit()
        elif unit == TemperatureUnit.K:
            return self.ToKelvin()

    def ToCelsius(self):
        if self.Unit == TemperatureUnit.C:
            return self
        elif self.Unit == TemperatureUnit.F:
            return Temperature((self.Value - 32) * 5.0 / 9.0, TemperatureUnit.C)
        elif self.Unit == TemperatureUnit.K:
            return Temperature(self.Value - 273.15, TemperatureUnit.C)

    def ToFahrenheit(self):
        if self.Unit == TemperatureUnit.F:
            return self
        elif self.Unit == TemperatureUnit.C:
            return Temperature(self.Value * 9 / 5 + 32, TemperatureUnit.F)
        elif self.Unit == TemperatureUnit.K:
            return Temperature((self.Value - 273.15) * 9 / 5 + 32, TemperatureUnit.F)

    def ToKelvin(self):
        if self.Unit == TemperatureUnit.K:
            return self
        elif self.Unit == TemperatureUnit.C:
            return Temperature(self.Value + 273.15, TemperatureUnit.K)
        elif self.Unit == TemperatureUnit.F:
            return Temperature((self.Value - 32) * 5.0 / 9.0 + 273.15, TemperatureUnit.K)