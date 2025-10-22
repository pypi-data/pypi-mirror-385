from biosero.datamodels.ordering import Order, ModuleRestrictionStrategy, SchedulingStrategy

from biosero.datamodels.ordering import Order, ModuleRestrictionStrategy, SchedulingStrategy
from biosero.datamodels.parameters import Parameter, ParameterCollection, ParameterValueType
from biosero.datamodels.restclients import OrderClient

from datetime import datetime

order_client = OrderClient(url="http://10.0.0.234:8105")


order = Order()
order.restrictToModuleIds = "Workflow Execution Engine"
order.templateName = "Library Preparation" 
order.moduleRestrictionStrategy = ModuleRestrictionStrategy.UnlessBusy
order.schedulingStrategy = "FirstAvailableSlot"

order.createdBy = "Test"

order.scheduledStartTime = datetime.now()

# p = Parameter()
# p.name = "Barcode"
# p.value = "BC-0001"
# p.valueType = ParameterValueType.STRING

# pc = ParameterCollection()
# pc.append(p)

# order.inputParameters = pc


order = order_client.create_order(order)
