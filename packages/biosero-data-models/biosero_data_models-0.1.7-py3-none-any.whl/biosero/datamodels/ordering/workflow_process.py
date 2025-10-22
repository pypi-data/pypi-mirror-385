import dataclasses
import json
from biosero.datamodels.parameters.parameter_collection import ParameterCollection

@dataclasses.dataclass
class WorkflowProcess:
    workflowProcessId: int = 0
    orderIdentifier: str = ''
    isPaused: bool = False
    globalVariables: ParameterCollection = dataclasses.field(default_factory=ParameterCollection)

    @classmethod
    def from_workflow_process(cls, workflow_process):
        obj = cls(**workflow_process)
        obj.globalVariables = json.loads(json.dumps(obj.globalVariables))
        return obj

    def to_workflow_process(self):
        wp = WorkflowProcess(**self.__dict__)
        wp.globalVariables = json.loads(json.dumps(wp.globalVariables))
        return wp
