import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, List

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

from biosero.datamodels.ordering import Order
from biosero.datamodels.restclients.order_client import OrderClient, OrderStatus
from biosero.dataservices.restclient import TransportationClient

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Rich console for live spinners
console = Console()

class OrderScheduler:
    def __init__(self, ds_url: str, demo: bool = False):
        self.ds_url = ds_url
        self.demo = demo
        self.order_client = OrderClient(ds_url)
        self.transportation_client = TransportationClient(ds_url)
        self.executor = ThreadPoolExecutor()

    async def close(self):
        if hasattr(self.order_client, "close") and callable(self.order_client.close):
            await self.order_client.close()
        if hasattr(self.transportation_client, "close") and callable(self.transportation_client.close):
            await self.transportation_client.close()

    def schedule_order(self, order: Order, wait: bool = True) -> asyncio.Task:
        logger.info(f"🚀 Starting schedule for order: {order.identifier} (template: {order.templateName})")

        input_params, output_params = self.get_template_parameters_by_name(order.templateName)
        order.outputParameters = output_params

        return asyncio.create_task(self._schedule_order_async(order, wait))

    async def initiate_workflow(
        self, 
        workflow_template_name: str, 
        input_parameters: Optional[List[dict]] = None,
        identifier: Optional[str] = None,
        created_by: Optional[str] = None,
        notes: Optional[str] = None,
        wait: bool = True
    ) -> Order:
        """
        Initiates a workflow by creating a parent order that will serve as the root for child orders.
        
        Args:
            workflow_template_name: Name of the workflow template to execute
            input_parameters: List of input parameters for the workflow
            identifier: Optional custom identifier for the workflow order
            created_by: Username or system that initiated the workflow
            notes: Optional notes for the workflow order
            wait: Whether to wait for workflow completion
            
        Returns:
            The completed workflow order (Order object)
        """
        logger.info(f"🔄 Initiating workflow: {workflow_template_name}")
        
        # Create the workflow parent order
        workflow_order = Order(
            identifier=identifier,
            templateName=workflow_template_name,
            inputParameters=input_parameters or [],
            createdBy=created_by,
            notes=notes or f"Workflow initiated: {workflow_template_name}"
        )
        
        # Get template parameters for the workflow
        input_params, output_params = self.get_template_parameters_by_name(workflow_template_name)
        workflow_order.outputParameters = output_params
        
        return await self._initiate_workflow_async(workflow_order, wait)

    async def _initiate_workflow_async(self, workflow_order: Order, wait: bool = True) -> Order:
        """
        Internal async method to initiate a workflow and return the complete order.
        
        Returns:
            The completed workflow order (Order object)
        """
        loop = asyncio.get_event_loop()
        workflow_order_id = await loop.run_in_executor(self.executor, self.order_client.create_order, workflow_order)
        
        self.order_client.update_order_status(workflow_order_id,OrderStatus.Running, "Workflow started")


        logger.info(f"📝 Created workflow order: {workflow_order_id}")
        
        if wait:
            await self._wait_for_completion(workflow_order_id)
        
        final_order = await loop.run_in_executor(self.executor, self.order_client.get_order, workflow_order_id)
        logger.info(f"✅ Workflow {workflow_order_id} completed with status: {final_order.status}")
        return final_order

    def complete_workflow(self, order: Order, details: Optional[str] = None) -> None:
        """
        Completes a workflow by updating its status to Complete.
        
        Args:
            order: The workflow order to complete
            details: Optional details about the completion
        """
        if not order.identifier:
            raise ValueError("Order must have an identifier to be completed")
        
        completion_details = details or f"Workflow {order.templateName} completed successfully"
        
        logger.info(f"🏁 Completing workflow: {order.identifier}")
        
        try:
            self.order_client.update_order_status(
                order_id=order.identifier,
                status=OrderStatus.Complete,
                details=completion_details
            )
            logger.info(f"✅ Workflow {order.identifier} marked as completed")
        except Exception as e:
            logger.error(f"❌ Failed to complete workflow {order.identifier}: {str(e)}")
            raise

    def get_template_parameters_by_name(self, name: str) -> Optional[Tuple[List[dict], List[dict]]]:
        templates = self.order_client.get_order_templates(limit=1000, offset=0)

        for template in templates:
            if template.Name and template.Name.lower() == name.lower():
                return template.InputParameters or [], template.OutputParameters or []

        logger.warning(f"⚠️ Template not found for: {name}")
        return None

    async def _schedule_order_async(self, order: Order, wait: bool = True) -> Order:
        loop = asyncio.get_event_loop()
        order_id = await loop.run_in_executor(self.executor, self.order_client.create_order, order)

        logger.info(f"📝 Created order: {order_id}")

        if wait:
            await self._wait_for_completion(order_id)

        final_order = await loop.run_in_executor(self.executor, self.order_client.get_order, order_id)
        logger.info(f"✅ Order {order_id} completed with status: {final_order.status}")
        return final_order

    async def _wait_for_completion(self, order_id: str, poll_interval: int = 5) -> None:
        loop = asyncio.get_event_loop()

        def get_status():
            return self.order_client.get_order_status(order_id)

        status = await loop.run_in_executor(self.executor, get_status)
        logger.info(f"⏳ Waiting for order {order_id} to complete... (current: {status.name})")

        if self.demo:
            spinner = Spinner("dots12", text=f"Order ID {order_id} in progress...")
            with Live(spinner, refresh_per_second=10, console=console):
                while status.name != "Complete":
                    await asyncio.sleep(poll_interval)
                    status = await loop.run_in_executor(self.executor, get_status)
                    spinner.text = f"Order ID {order_id}: {status.name}..."
        else:
            while status.name != "Complete":
                await asyncio.sleep(poll_interval)
                status = await loop.run_in_executor(self.executor, get_status)
                logger.info(f"Order ID {order_id}: {status.name}...")

        logger.info(f"✅ Order {order_id} completed.")

    def request_transfer(
        self,
        source_station_id: str,
        destination_station_id: str,
        item_ids: List[str],
        order_id: str,
        metadata: str,
        created_by: str,
        wait: bool = True,
    ) -> asyncio.Task:
        logger.info(f"🚚 Starting transfer for order: {order_id} | From: {source_station_id} -> To: {destination_station_id}")
        return asyncio.create_task(
            self._request_transfer_async(
                source_station_id,
                destination_station_id,
                item_ids,
                order_id,
                metadata,
                created_by,
                wait,
            )
        )

    async def _request_transfer_async(
        self,
        source_station_id: str,
        destination_station_id: str,
        item_ids: List[str],
        order_id: str,
        metadata: str,
        created_by: str,
        wait: bool = True,
    ) -> str:
        loop = asyncio.get_event_loop()

        def submit_transfer():
            return self.transportation_client.requestTransfer(
                sourceStationId=source_station_id,
                destinationStationId=destination_station_id,
                itemIds=item_ids,
                orderId=order_id,
                metadata=metadata,
                createdBy=created_by,
            )

        tr_id = await loop.run_in_executor(self.executor, submit_transfer)
        logger.info(f"📝 Submitted transfer request: {tr_id}")

        if wait:
            await self._wait_for_transfer(tr_id)

        return tr_id

    async def _wait_for_transfer(self, transfer_id: str, poll_interval: int = 5) -> None:
        loop = asyncio.get_event_loop()

        def get_status():
            return self.transportation_client.getStatus(transfer_id)

        status = await loop.run_in_executor(self.executor, get_status)
        logger.info(f"⏳ Waiting for transfer {transfer_id} to complete... (current: {status.name})")

        if self.demo:
            spinner = Spinner("dots12", text=f"Transfer ID {transfer_id} in progress...")
            with Live(spinner, refresh_per_second=10, console=console):
                while status.name != "Complete":
                    await asyncio.sleep(poll_interval)
                    status = await loop.run_in_executor(self.executor, get_status)
                    spinner.text = f"Transfer ID {transfer_id}: {status.name}..."
        else:
            while status.name != "Complete":
                await asyncio.sleep(poll_interval)
                status = await loop.run_in_executor(self.executor, get_status)
                logger.info(f"Transfer ID {transfer_id}: {status.name}...")

        logger.info(f"✅ Transfer {transfer_id} complete.")
