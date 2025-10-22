from dataclasses import dataclass, field, asdict
from typing import Generic, TypeVar, Optional
from biosero.datamodels.events import EventContext

T = TypeVar('T')

@dataclass
class Event(Generic[T]):
    
    context: EventContext = field(default_factory=EventContext)
    data: Optional[T] = None

    def __init__(self, data: Optional[T] = None, context: Optional[EventContext] = None):
        if context is None:
            context = EventContext()
        self.context = context
        self.data = data

    def __str__(self):
        return f"Event(context={self.context}, data={self.data})"
    def to_dict(self):
        """Converts the Event instance to a dictionary."""
        return asdict(self)