from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime

class IOrderClient(ABC):
    
    @abstractmethod
    def create_order(self, order: 'Order') -> str:
        """
        Creates the specified order.

        :param order: The order.
        :return: System.String representing the assigned OrderId.
        """
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> 'OrderStatus':
        """
        Gets the order status of the order with the specified orderId parameter.

        :param order_id: The order identifier.
        :return: OrderStatus.
        """
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> 'Order':
        """
        Gets the order with the specified by the orderId property.

        :param order_id: The order identifier.
        :return: Order.
        """
        pass

    @abstractmethod
    def get_unassigned_orders(self, limit: int, offset: int) -> List['Order']:
        """
        Gets the unassigned orders. These are orders that are ready for execution but have not had a module or process assigned to execute them.

        :param limit: The limit.
        :param offset: The offset.
        :return: List of orders containing all unassigned orders.
        """
        pass

    @abstractmethod
    def get_executing_orders(self, limit: int, offset: int) -> List['Order']:
        """
        Gets an array of all the currently executing orders.

        :param limit: The limit.
        :param offset: The offset.
        :return: List of orders containing all the currently executing orders.
        """
        pass

    @abstractmethod
    def get_completed_orders(self, limit: int, offset: int) -> List['Order']:
        """
        Gets the completed orders. The limit parameter specified the number to fetch, and the offset specifies how many to skip. This provides basic pagination.

        :param limit: The limit specifies the number of orders to fetch.
        :param offset: The offset specifies the number of orders to skip.
        :return: List of orders.
        """
        pass

    @abstractmethod
    def get_orders(self, created_on_or_before: datetime, limit: int, offset: int) -> List['Order']:
        """
        Gets the orders created on or before the specified DateTimeOffset

        :param created_on_or_before: The created on or before.
        :param limit: The limit specifies the number of orders to fetch.
        :param offset: The offset specifies the number of orders to skip.
        :return: List of orders.
        """
        pass

    @abstractmethod
    def try_assign_order(self, order_id: str, identifier_to_assign_to: str) -> bool:
        """
        Attempts to assign the order to the specified module or process (identifier_to_assign_to).

        :param order_id: The order identifier.
        :param identifier_to_assign_to: The identifier to assign to.
        :return: True if the assignment succeeded, False otherwise.
        """
        pass

    @abstractmethod
    def update_order_status(self, order_id: str, status: 'OrderStatus', details: str):
        """
        Updates the order status with the specified status and status details.

        :param order_id: The order identifier.
        :param status: The status.
        :param details: The status details.
        """
        pass

    @abstractmethod
    def set_output_parameters(self, order_id: str, parameters: Dict[str, str]):
        """
        Sets the output parameters of the order. This is called once the execution has completed but before the order status has been changed to completed in order to ensure the output parameters are set when the status changes.

        :param order_id: The order identifier.
        :param parameters: The parameters.
        """
        pass

    @abstractmethod
    def update_order(self, order: 'Order'):
        """
        Updates all properties of the order in the database to the values of the specified order.

        :param order: The order.
        """
        pass

    @abstractmethod
    def persist_state(self, order_id: str, state: str):
        """
        Updates the State property of the order specified by the orderId parameter. This is used to persist the state of an ongoing order.

        :param order_id: The order identifier.
        :param state: The state.
        """
        pass

    @abstractmethod
    def get_order_templates(self, limit: int, offset: int) -> List['OrderTemplate']:
        """
        Gets all available order templates.

        :param limit: The limit.
        :param offset: The offset.
        :return: List of order templates.
        """
        pass

    @abstractmethod
    def register_order_template(self, template: 'OrderTemplate'):
        """
        Registers a new order template.

        :param template: The template.
        """
        pass

    @abstractmethod
    def delete_order_template(self, template_name: str):
        """
        Deletes the order template specified by the provided templateName.

        :param template_name: Name of the template.
        """
        pass
