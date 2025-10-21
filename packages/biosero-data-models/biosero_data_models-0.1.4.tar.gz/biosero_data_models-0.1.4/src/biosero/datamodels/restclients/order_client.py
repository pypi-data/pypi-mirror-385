import json
import requests

#import asyncio
from urllib.parse import urlencode
from datetime import datetime
from typing import List, Dict
from biosero.datamodels.clients import IOrderClient
from biosero.datamodels.helpers import HttpClientHelper
from biosero.datamodels.ordering import Order, OrderTemplate, OrderStatus
from biosero.datamodels.restclients.dtos import OrderDto


class OrderClient(IOrderClient):
    def __init__(self, url: str = None, url_provider: callable = None, http_client: requests.Session = None):
        if url:
            self._http_client = HttpClientHelper.configure_http_client(url)
            self._base_url = url
        elif url_provider:
            self._http_client = HttpClientHelper.configure_http_client(url_provider())
            self._base_url = url_provider()
        elif http_client:
            self._http_client = http_client
            self._base_url = http_client.base_url
        else:
            raise ValueError("You must provide either a url, url_provider, or http_client.")

    def dispose(self):
        self._http_client.close()

    def create_order(self, order: Order) -> str:
        path = f"{self._base_url}/api/v2.0/OrderService/CreateOrder"
        dto = OrderDto.from_order(order)
        #dto_dict = dto.to_dict()  # Convert to dictionary
        dto_dict = {k: v for k, v in dto.to_dict().items() if v is not None}
        response = self._http_client.post(path, json=dto_dict)
        response.raise_for_status()
        return response.json()

    def delete_order_template(self, template_name: str):
        path = f"{self._base_url}/api/v2.0/OrderService/DeleteOrderTemplate?templateName={urlencode({'templateName': template_name})}"
        response = self._http_client.delete(path)
        response.raise_for_status()

    def get_completed_orders(self, limit: int, offset: int) -> List[Order]:
        path = f"{self._base_url}/api/v2.0/OrderService/CompletedOrders?limit={limit}&offset={offset}"
        response = self._http_client.get(path)
        response.raise_for_status()
        return [Order(**order) for order in response.json()]

    def get_executing_orders(self, limit: int, offset: int) -> List[Order]:
        path = f"{self._base_url}/api/v2.0/OrderService/ExecutingOrders?limit={limit}&offset={offset}"
        response = self._http_client.get(path)
        response.raise_for_status()
        return [Order(**order) for order in response.json()]

    # def get_order(self, order_id: str) -> Order:
    #     path = f"{self._base_url}/api/v2.0/OrderService/Order?{urlencode({'orderId': order_id})}"
    #     response = self._http_client.get(path)
    #     response.raise_for_status()
    #     return Order(**response.json())
    
    def get_order(self, order_id: str) -> Order:
        path = f"{self._base_url}/api/v2.0/OrderService/Order?{urlencode({'orderId': order_id})}"
        response = self._http_client.get(path)
        response.raise_for_status()
        order_data = response.json()
        return Order.from_dict(order_data)

    # def get_orders(self, created_on_or_before: datetime, limit: int, offset: int) -> List[Order]:
    #     date_time = created_on_or_before.isoformat()
    #     path = f"{self._base_url}/api/v2.0/OrderService/Orders?{urlencode({'createdOnOrBefore': date_time})}&limit={limit}&offset={offset}"
    #     response = self._http_client.get(path)
    #     response.raise_for_status()
    #     return [Order(**order) for order in response.json()]
    
    def get_orders(self, created_on_or_before: datetime, limit: int, offset: int) -> List[Order]:
        date_time = created_on_or_before.isoformat()
        path = f"{self._base_url}/api/v2.0/OrderService/Orders?{urlencode({'createdOnOrBefore': date_time})}&limit={limit}&offset={offset}"
        response = self._http_client.get(path)
        response.raise_for_status()
        return [Order.from_dict(order) for order in response.json()]

    def get_order_status(self, order_id: str) -> OrderStatus:
        path = f"{self._base_url}/api/v2.0/OrderService/OrderStatus?{urlencode({'orderId': order_id})}"
        response = self._http_client.get(path)
        response.raise_for_status()
        status = response.json()
        return OrderStatus[status]

    def get_order_templates(self, limit: int, offset: int) -> List[OrderTemplate]:
        path = f"{self._base_url}/api/v2.0/OrderService/OrderTemplates?limit={limit}&offset={offset}"
        response = self._http_client.get(path)
        response.raise_for_status()
        
        return [OrderTemplate.from_dict(template) for template in response.json()]
        #return [OrderTemplate(**template) for template in response.json()]

    def get_unassigned_orders(self, limit: int, offset: int) -> List[Order]:
        path = f"{self._base_url}/api/v2.0/OrderService/UnassignedOrders?limit={limit}&offset={offset}"
        response = self._http_client.get(path)
        response.raise_for_status()
        #return [Order(**order) for order in response.json()]
        return [Order.from_dict(order) for order in response.json()]
    

    def persist_state(self, order_id: str, state: str):
        path = f"{self._base_url}/api/v2.0/OrderService/PersistState?{urlencode({'orderId': order_id})}"
        response = self._http_client.post(path, json=state)
        response.raise_for_status()

    def register_order_template(self, template: OrderTemplate):
        path = f"{self._base_url}/api/v2.0/OrderService/RegisterOrderTemplate"
        template_dict = template.to_dict()
        template_json = json.dumps(template_dict)
        response = self._http_client.post(path, json=template_dict)
        response.raise_for_status()

    def set_output_parameters(self, order_id: str, parameters: Dict[str, str]):
        path = f"{self._base_url}/api/v2.0/OrderService/SetOutputParameters?orderId={urlencode({'orderId': order_id})}"
        response = self._http_client.post(path, json=parameters)
        response.raise_for_status()

    def try_assign_order(self, order_id: str, identifier_to_assign_to: str) -> bool:
        path = f"{self._base_url}/api/v2.0/OrderService/TryAssignOrder?orderId={urlencode({'orderId': order_id})}&to={urlencode({'to': identifier_to_assign_to})}"
        response = self._http_client.post(path)
        response.raise_for_status()
        return response.json()

    def update_order(self, order: Order):
        path = f"{self._base_url}/api/v2.0/OrderService/UpdateOrder"
        response = self._http_client.post(path, json=order)
        response.raise_for_status()

    def update_order_status(self, order_id: str, status: OrderStatus, details: str):
        from urllib.parse import quote
        path = f"{self._base_url}/api/v2.0/OrderService/UpdateOrderStatus?orderId={quote(order_id)}&status={quote(status.name)}"
        response = self._http_client.post(path, json=details)
        response.raise_for_status()

    def get_order_descendants_and_self(self, order_id: str) -> List[Order]:
        """Get an order and all its descendant orders."""
        path = f"{self._base_url}/api/v3.0/orders/{order_id}/descendants-and-self"
        response = self._http_client.get(path)
        response.raise_for_status()
        return [Order.from_dict(order) for order in response.json()]

    def get_parameter_value(self, parameters, name):
        return next((param['value'] for param in parameters if param['name'] == name), None)

    async def close(self):
        if hasattr(self._http_client, "close") and callable(self._http_client.close):
            self._http_client.close()
