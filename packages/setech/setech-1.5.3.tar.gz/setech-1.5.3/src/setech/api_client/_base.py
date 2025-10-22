import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Coroutine
from typing import Any

import httpx
from httpx._types import URLTypes

from setech.utils import SetechJSONEncoder, get_logger, get_nonce

_TypeSyncAsyncResponse = httpx.Response | Coroutine[Any, Any, httpx.Response]


class BaseClient(ABC):
    base_url: URLTypes
    _session: httpx._client.BaseClient
    _nonce: str
    _logger: logging.Logger
    json_encoder: type[json.JSONEncoder] = SetechJSONEncoder

    def __init__(self, nonce: str = "", session: httpx._client.BaseClient | None = None):
        self._nonce = nonce or get_nonce()
        self._session = session or httpx.Client()
        self._logger = get_logger("APIClient")

    @abstractmethod
    def get(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        """
        Send a `GET` request.

        :param endpoint: Endpoint path to which to make request
        :param params: See `httpx.Request`.
        **Parameters**: See `httpx.Request`.
        """

    @abstractmethod
    def post(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        """
        Send a `POST` request.

        :param endpoint: Endpoint path to which to make request
        :param data: See `httpx.Request`
        :param json: See `httpx.Request`
        **Parameters**: See `httpx.Request`.
        """

    @abstractmethod
    def put(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        """
        Send a `PUT` request.

        :param endpoint: Endpoint path to which to make request
        :param data: See `httpx.Request`
        :param json: See `httpx.Request`
        **Parameters**: See `httpx.Request`.
        """

    @abstractmethod
    def patch(self, endpoint: str, *, json: Any = None, data: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        """
        Send a `PATCH` request.

        :param endpoint: Endpoint path to which to make request
        :param data: See `httpx.Request`
        :param json: See `httpx.Request`
        **Parameters**: See `httpx.Request`.
        """

    @abstractmethod
    def delete(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        """
        Send a `DELETE` request.

        :param endpoint: Endpoint path to which to make request
        :param params: See `httpx.Request`.
        :param kwargs: See `httpx.Request`.
        """

    @abstractmethod
    def head(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        """
        Send a `HEAD` request.

        :param endpoint: Endpoint path to which to make request
        :param params: See `httpx.Request`.
        **Parameters**: See `httpx.Request`.
        """

    @abstractmethod
    def options(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        """
        Send a `OPTIONS` request.

        :param endpoint: Endpoint path to which to make request
        :param params: See `httpx.Request`.
        **Parameters**: See `httpx.Request`.
        """

    @abstractmethod
    def trace(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        """
        Send a `TRACE` request.

        :param endpoint: Endpoint path to which to make request
        :param params: See `httpx.Request`.
        **Parameters**: See `httpx.Request`.
        """

    @abstractmethod
    def connect(self, endpoint: str, *, params: Any = None, **kwargs: Any) -> _TypeSyncAsyncResponse:
        """
        Send a `CONNECT` request.

        :param endpoint: Endpoint path to which to make request
        :param params: See `httpx.Request`.
        **Parameters**: See `httpx.Request`.
        """

    @abstractmethod
    def _request(self, method: str, endpoint: str, **kwargs: Any) -> _TypeSyncAsyncResponse:
        pass

    @abstractmethod
    def before_request(self, request: httpx.Request) -> None:
        """
        Hook to execute additional tasks just before request is sent.

        :param request: See `httpx.Request`.
        """

    @abstractmethod
    def after_request(self, response: httpx.Response) -> None:
        """
        Hook to execute additional tasks just after the response has been received.

        :param response: See `httpx.Response`.
        """

    def _make_full_url(self, endpoint: str) -> str:
        if self._session.base_url:
            return endpoint
        return f"{self.base_url}{endpoint}"

    def prepare_authentication(self, request: httpx.Request) -> httpx.Request:
        """
        Hook to authentication for the request.

        :rtype: httpx.Request
        :param request: See `httpx.Request`.
        """
        return request

    def _prepare_request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Request:
        full_url = self._make_full_url(endpoint)
        if kwargs.get("json"):
            kwargs["json"] = json.loads(json.dumps(kwargs["json"], cls=self.json_encoder))
        self._debug_log_request(method, full_url, 4)
        request: httpx.Request = self._session.build_request(method=method, url=full_url, **kwargs)
        self._info_log_request_sending(request, 4)
        return request

    def _debug_log_request(self, method: str, full_url: str, stacklevel: int = 5) -> None:
        self._debug(f"Preparing {method} request for '{full_url}'", stacklevel=stacklevel + 1)

    def _debug_log_prepared_request(self, request: httpx.Request, stacklevel: int = 5) -> None:
        self._debug(
            f"Prepared {request.method} request to '{request.url}'",
            extra={"request": request},
            stacklevel=stacklevel + 1,
        )

    def _info_log_request_sending(self, request: httpx.Request, stacklevel: int = 5) -> None:
        self._info(
            f"Sending {request.method} request to '{request.url}'",
            extra={"request": request},
            stacklevel=stacklevel + 1,
        )

    def _info_log_response(self, response: httpx.Response, stacklevel: int = 5) -> None:
        self._info(f"Response {response.status_code=}", extra={"response": response}, stacklevel=stacklevel + 1)

    def _debug(self, msg: str, stacklevel: int, *args: Any, **kwargs: Any) -> None:
        self._log("DEBUG", f"[{self._nonce}] {msg}", stacklevel=stacklevel + 1, *args, **kwargs)  # noqa: B026

    def _info(self, msg: str, stacklevel: int, *args: Any, **kwargs: Any) -> None:
        self._log("INFO", f"[{self._nonce}] {msg}", stacklevel=stacklevel + 1, *args, **kwargs)  # noqa: B026

    def _warn(self, msg: str, stacklevel: int, *args: Any, **kwargs: Any) -> None:
        self._log("WARNING", f"[{self._nonce}] {msg}", stacklevel=stacklevel + 1, *args, **kwargs)  # noqa: B026

    def _error(self, msg: str, stacklevel: int, *args: Any, **kwargs: Any) -> None:
        self._log("ERROR", f"[{self._nonce}] {msg}", stacklevel=stacklevel + 1, *args, **kwargs)  # noqa: B026

    def _critical(self, msg: str, stacklevel: int, *args: Any, **kwargs: Any) -> None:
        self._log("CRITICAL", f"[{self._nonce}] {msg}", stacklevel=stacklevel + 1, *args, **kwargs)  # noqa: B026

    def _log(
        self, level: str, msg: object, *args: object, stacklevel: int, extra: dict | None = None, **kwargs: Any
    ) -> None:
        extra = extra or {}
        extra.update(nonce=self._nonce)
        self._logger.log(
            logging.getLevelNamesMapping()[level], msg, *args, stacklevel=stacklevel + 1, extra=extra, **kwargs
        )
