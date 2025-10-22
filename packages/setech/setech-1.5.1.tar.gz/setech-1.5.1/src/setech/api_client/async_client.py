from abc import ABC
from typing import Any

import httpx

from ._base import BaseClient


class AsyncClient(BaseClient, ABC):
    _session: httpx.AsyncClient

    def __init__(self, nonce: str = "", session: httpx.AsyncClient | None = None):
        super().__init__(nonce, session or httpx.AsyncClient(http2=True, base_url=self.base_url))

    async def get(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def post(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> httpx.Response:
        return await self._request("POST", endpoint, json=json, data=data, **kwargs)

    async def put(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> httpx.Response:
        return await self._request("PUT", endpoint, json=json, data=data, **kwargs)

    async def patch(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> httpx.Response:
        return await self._request("GET", endpoint, json=json, data=data, **kwargs)

    async def delete(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def head(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def options(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def trace(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def connect(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> httpx.Response:
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:
        request = self._prepare_request(method, endpoint, **kwargs)
        self.before_request(request)
        response = await self._session.send(request, auth=self.prepare_authentication)
        self._info_log_response(response, 4)
        self.after_request(response)

        return response
