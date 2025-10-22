
import datetime
from biosero.datamodels.resources import Identity
from biosero.datamodels.events import EventContext
from biosero.dataservices.restclient import AccessioningClient
from biosero.datamodels import ParameterCollection 



class Registration:

    def __init__(self, url: str):
        """Initialize Registration with a URL."""
        self.url = url
        self.accessioning_client = AccessioningClient(url)

    def register_identity(self, identifier: str, name: str, type_identifier: str, paramter_collection: ParameterCollection, description: str = "", is_instance: bool = True, inherits_properties:bool = True) -> Identity:
        """Register an identity."""
        identity = Identity()
        identity.identifier = identifier
        identity.name = name
        identity.typeIdentifier = type_identifier
        identity.properties = paramter_collection
        identity.isInstance = is_instance
        identity.inheritProperties = inherits_properties
        identity.description = description
        event_context = EventContext()
        event_context.ActorId ="Python Script"
        event_context.Start = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

       

        self.accessioning_client.register(identity, event_context)

        return identity
    
    def register_many_identities(self, identities: list[Identity]) -> None:
        """Register multiple identities in a single call."""
        event_context = EventContext()
        event_context.ActorId = "Python Script"
        event_context.Start = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        self.accessioning_client.register_many(identities, event_context)