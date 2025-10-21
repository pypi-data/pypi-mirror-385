"""
Example usage of the workflow functionality in OrderScheduler.

This example demonstrates how to:
1. Initiate a workflow (parent order)
2. Schedule child orders under that workflow
3. Monitor workflow progress and status
"""

import asyncio
from biosero.datamodels.ordering import Order
from biosero.datamodels.restclients.order_scheduler import OrderScheduler


async def workflow_example():
    """
    Example of initiating a workflow and scheduling child orders.
    """
    # Initialize the order scheduler
    scheduler = OrderScheduler("http://10.0.0.234:8105", demo=True)
    
    try:
        # 1. Initiate a workflow (creates a parent order)
        workflow_task = await scheduler.initiate_workflow(
            workflow_template_name="Cell Culture Workflow",
            input_parameters=[
                {"name": "sample_count", "value": "10"},
                {"name": "protocol_id", "value": "PROT-001"}
            ],
            created_by="workflow_user",
            notes="Automated workflow for sample processing",
            wait=False  # Don't wait for workflow completion yet
        )
        
        # Get the workflow order
   
        workflow_id = workflow_task.identifier

        scheduler.complete_workflow(workflow_task)


        print(f"✅ Workflow initiated with ID: {workflow_id}")
        
        # 2. Schedule child orders under this workflow

        return "final_summary"
        
    finally:
        # Clean up resources
        await scheduler.close()


async def simple_workflow_example():
    """
    Simplified example for basic workflow usage.
    """
    scheduler = OrderScheduler("http://your-data-services-url")
    
    try:
        # Create and execute a simple workflow
        workflow_order = await scheduler.initiate_workflow(
            workflow_template_name="SimpleWorkflow",
            input_parameters=[{"name": "input_data", "value": "test_data"}],
            created_by="user123",
            wait=True  # Wait for workflow to complete
        )
        
        print(f"Workflow {workflow_order.identifier} completed with status: {workflow_order.status}")
        
        # Create a child order
        child_order = Order(
            templateName="ProcessingStep",
            inputParameters=[{"name": "data_source", "value": "workflow_output"}],
            createdBy="user123"
        )
        
        completed_child = await scheduler.schedule_child_order(
            order=child_order,
            parent_workflow_id=workflow_order.identifier,
            wait=True
        )
        
        print(f"Child order {completed_child.identifier} completed")
        
    finally:
        await scheduler.close()


if __name__ == "__main__":
    # Run the comprehensive example
    asyncio.run(workflow_example())
    
    # Or run the simple example
    # asyncio.run(simple_workflow_example())