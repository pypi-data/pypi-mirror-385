import requests
from typing import Callable

class HttpClientHelper:
    @staticmethod
    def configure_http_client(url: str) -> requests.Session:
        if not url.endswith("/"):
            url += "/"

        session = requests.Session()
        session.base_url = url
        session.headers.update({
            'Accept': 'application/json'
        })

        return session

    @staticmethod
    def configure_http_client_from_provider(url_provider: Callable[[], str]) -> requests.Session:
        return HttpClientHelper.configure_http_client(url_provider())

# Usage example:

def url_provider():
    return "https://api.example.com"
