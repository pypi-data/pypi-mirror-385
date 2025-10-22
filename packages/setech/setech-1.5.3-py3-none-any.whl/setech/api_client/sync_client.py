from abc import ABC
from typing import Any

import httpx

from ._base import BaseClient


class SyncClient(BaseClient, ABC):
    _session: httpx.Client

    def __init__(self, nonce: str = "", session: httpx.Client | None = None):
        super().__init__(nonce, session or httpx.Client(http2=True, base_url=self.base_url))

    def get(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> httpx.Response:
        return self._request("POST", endpoint, json=json, data=data, **kwargs)

    def put(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> httpx.Response:
        return self._request("PUT", endpoint, json=json, data=data, **kwargs)

    def patch(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> httpx.Response:
        return self._request("PATCH", endpoint, json=json, data=data, **kwargs)

    def delete(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return self._request("DELETE", endpoint, params=params, **kwargs)

    def head(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return self._request("HEAD", endpoint, params=params, **kwargs)

    def options(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return self._request("OPTIONS", endpoint, params=params, **kwargs)

    def trace(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return self._request("TRACE", endpoint, params=params, **kwargs)

    def connect(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return self._request("CONNECT", endpoint, params=params, **kwargs)

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:
        request = self._prepare_request(method, endpoint, **kwargs)
        self.before_request(request)
        response = self._session.send(request, auth=self.prepare_authentication)
        self._info_log_response(response)
        self.after_request(response)

        return response
