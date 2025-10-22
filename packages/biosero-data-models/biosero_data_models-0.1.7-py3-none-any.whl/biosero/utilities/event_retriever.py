import json
from biosero.dataservices.restclient.queryclient import QueryClient
from biosero.datamodels.events import EventSearchParameters

class InstrumentEventRetriever:
    def __init__(self,data_services_url:str, association_id: str, module_id: str):
        self.query_client = QueryClient(url=data_services_url)
        self.association_id = association_id
        self.module_id = module_id

    def get_instrument_events(self, actor_id: str = None, workcell_process: str = None, instrument_process: str = None, instrument_name: str = None, operation: str = None, subjects: list = None, limit: int = 10000, offset: int = 0):
        
        parameters = EventSearchParameters(
            AssociationId=self.association_id,
            Topic="Biosero.DataModels.Events.InstrumentOperationEvent",
            ModuleId=self.module_id,
            ActorId=actor_id,
        )

        events = self.query_client.get_events(search_parameters=parameters, limit=limit, offset=offset)

        filtered_events = []
        for event in events:
            data = json.loads(event.Data)
            if workcell_process is not None and data.get("workcellProcess") != workcell_process:
                continue
            if instrument_process is not None and data.get("instrumentProcess") != instrument_process:
                continue
            if instrument_name is not None and data.get("instrumentName") != instrument_name:
                continue
            if subjects is not None and event.Subjects != subjects:
                continue
            if operation is not None and data.get("operation") != operation:
                continue
            filtered_events.append(event)

        return filtered_events