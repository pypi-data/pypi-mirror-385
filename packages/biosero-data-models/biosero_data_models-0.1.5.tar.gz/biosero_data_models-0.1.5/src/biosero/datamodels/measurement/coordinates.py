import json

class Coordinates:
    def __new__(cls, row: str, column: str):
        """
        Override the object creation process to return a JSON string instead of an object.
        """
        return json.dumps({"Row": row, "Column": column})
