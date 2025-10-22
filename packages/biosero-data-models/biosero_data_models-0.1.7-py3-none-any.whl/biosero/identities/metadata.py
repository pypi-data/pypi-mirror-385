from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class Coordinates:
    row: int
    column: int

    def __str__(self):
        return f"{self.row},{self.column}"

    def __repr__(self):
        return f"Coordinates(row={self.row}, column={self.column})"

    def to_serialized_string(self):
        return f"{self.row},{self.column}"

    @classmethod
    def from_serialized_string(cls, data: str):
        row, column = map(int, data.split(','))
        return cls(row=row, column=column)

    def to_well_name(self):
        """
        Convert to classic well name like 'A1', 'B3', etc.
        """
        return f"{chr(ord('A') + self.row - 1)}{self.column}"


def get_well_positions(rows: int, columns: int):
    """
    Returns a list of well names like ['A1', 'A2', ..., 'H12'].
    """
    return [f"{chr(ord('A') + row)}{col}" for row in range(rows) for col in range(1, columns + 1)]


def get_coordinates_strings(rows: int, columns: int):
    """
    Returns a list of 'row,column' strings like ['1,1', '1,2', ..., '8,12'].
    """
    return [Coordinates(row, col).to_serialized_string() for row in range(1, rows + 1) for col in range(1, columns + 1)]


class MetaData:

    @staticmethod
    def get_well_positions(rows: int, columns: int):
        return get_well_positions(rows, columns)

    @staticmethod
    def get_coordinates_strings(rows: int, columns: int):
        return get_coordinates_strings(rows, columns)

    class NinetySixWell(Enum):
        POSITIONS = get_well_positions(8, 12)
        COORDINATES = get_coordinates_strings(8, 12)
