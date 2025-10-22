import httpx

import setech

_LIB_USER_AGENT = f"Setech Utils v{setech.__version__} ({httpx._client.USER_AGENT})"


def get_httpx_client(
    *,
    sync: bool,
    base_url: str,
    to_read: float = 120,
    to_write: float = 120,
    user_agent: str = _LIB_USER_AGENT,
) -> httpx.Client | httpx.AsyncClient:
    """Method to generate a httpx Client instance to use for setech API Clients.

    :param sync: Should the return be a httpx.Client or httpx.AsyncClient
    :param base_url: Base URL to use for requests
    :param to_read: Seconds to wait for reading responses
    :param to_write: Seconds to wait for writing responses
    :param user_agent: User Agent string to use
    :return: httpx Client instance
    """
    if sync:
        return get_httpx_sync_client(base_url=base_url, to_read=to_read, to_write=to_write, user_agent=user_agent)
    return get_httpx_async_client(base_url=base_url, to_read=to_read, to_write=to_write, user_agent=user_agent)


def get_httpx_async_client(
    *,
    base_url: str,
    to_read: float = 120,
    to_write: float = 120,
    user_agent: str = _LIB_USER_AGENT,
) -> httpx.AsyncClient:
    """Method to generate a httpx AsyncClient instance to use for setech API Clients.

    :param base_url: Base URL to use for requests
    :param to_read: Seconds to wait for reading responses
    :param to_write: Seconds to wait for writing responses
    :param user_agent: User Agent string to use
    :return: `httpx.AsyncClient` instance
    """
    timeout = httpx.Timeout(60, read=to_read, write=to_write)
    return httpx.AsyncClient(base_url=base_url, http2=True, timeout=timeout, headers={"user-Agent": user_agent})


def get_httpx_sync_client(
    base_url: str,
    to_read: float = 120,
    to_write: float = 120,
    user_agent: str = _LIB_USER_AGENT,
) -> httpx.Client:
    """Method to generate a httpx AsyncClient instance to use for setech API Clients.

    :param base_url: Base URL to use for requests
    :param to_read: Seconds to wait for reading responses
    :param to_write: Seconds to wait for writing responses
    :param user_agent: User Agent string to use
    :return: `httpx.Client` instance
    """
    timeout = httpx.Timeout(60, read=to_read, write=to_write)
    return httpx.Client(base_url=base_url, http2=True, timeout=timeout, headers={"user-Agent": user_agent})
