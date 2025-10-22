from dataclasses import dataclass
from typing import List
from biosero.datamodels.events import EventContext
from biosero.datamodels.resources import Identity

@dataclass
class MultiIdentityRegistrationDto:
    identities: List[Identity]
    event_context: EventContext
