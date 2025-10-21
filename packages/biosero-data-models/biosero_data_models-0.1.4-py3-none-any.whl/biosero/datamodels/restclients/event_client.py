import json
import requests
import httpx
from dataclasses import asdict
from datetime import datetime
from typing import Callable, Optional

class HttpClientHelper:
    @staticmethod
    def configure_http_client(url: str) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        session.base_url = url if url.endswith('/') else f"{url}/"
        return session

    @staticmethod
    def configure_http_client_with_provider(url_provider: Callable[[], str]) -> requests.Session:
        return HttpClientHelper.configure_http_client(url_provider())

class EventClient:
    def __init__(self, url: Optional[str] = None, url_provider: Optional[Callable[[], str]] = None, http_client: Optional[requests.Session] = None):
        if url:
            self._http_client = HttpClientHelper.configure_http_client(url)
            self._created_client = True
        elif url_provider:
            self._http_client = HttpClientHelper.configure_http_client_with_provider(url_provider)
            self._created_client = True
        elif http_client:
            self._http_client = http_client
            self._created_client = False
        else:
            raise ValueError("Either url, url_provider, or http_client must be provided")

    def __del__(self):
        if self._created_client and self._http_client:
            self._http_client.close()


    async def publish_async(self, event_message: 'EventMessage', client: httpx.AsyncClient) -> str:
        url = f"{self._http_client.base_url}api/v2.0/EventService"

        event_message_dict = asdict(event_message)
        event_message_dict = self.remove_none_values(event_message_dict)

        response = await client.post(url, json=event_message_dict)
        response.raise_for_status()
        return response.content.decode('utf-8')


    def publish_event(self, event_message: 'EventMessage') -> str:
        url = f"{self._http_client.base_url}api/v2.0/EventService"
        event_message_dict = asdict(event_message)

        event_message_dict = self.remove_none_values(event_message_dict)

        # print(json.dumps(event_message_dict, indent=4))

        response = self._http_client.post(url, json=event_message_dict)

        raw_response = response.content.decode('utf-8')
        response.raise_for_status()
        
        return response.json()
    def remove_none_values(self, d: dict) -> dict:
        """Remove items with None values from the dictionary."""
        return {k: v for k, v in d.items() if v is not None}

    def get_server_time(self) -> datetime:
        return datetime.now()
    