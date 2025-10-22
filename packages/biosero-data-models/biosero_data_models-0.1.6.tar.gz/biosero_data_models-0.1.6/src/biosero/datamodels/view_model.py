from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List
import json

class PropertyChangedEvent:
    def __init__(self):
        self._handlers: List[Callable[[str], None]] = []

    def add(self, handler: Callable[[str], None]):
        self._handlers.append(handler)

    def remove(self, handler: Callable[[str], None]):
        self._handlers.remove(handler)

    def notify(self, property_name: str):
        for handler in self._handlers:
            handler(property_name)

@dataclass
class ViewModel:
    _property_changed: PropertyChangedEvent = field(default_factory=PropertyChangedEvent, init=False, repr=False)

    def on_property_changed(self, property_name: str):
        self._property_changed.notify(property_name)

    def set_field(self, field_name: str, value: Any):
        if hasattr(self, field_name):
            current_value = getattr(self, field_name)
            if current_value != value:
                setattr(self, field_name, value)
                self.on_property_changed(field_name)
                return True
        return False

    def add_property_changed_handler(self, handler: Callable[[str], None]):
        self._property_changed.add(handler)

    def remove_property_changed_handler(self, handler: Callable[[str], None]):
        self._property_changed.remove(handler)
