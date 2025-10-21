from dataclasses import dataclass
from biosero.datamodels.events import EventContext
from biosero.datamodels.resources import Identity

@dataclass
class IdentityRegistrationDto:
    identity: Identity
    event_context: EventContext
