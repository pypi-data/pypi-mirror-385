import logging
import uuid

from setech.constants import types

__all__ = ["get_ip", "get_logger", "get_nonce"]


def get_logger(name: str = "service") -> logging.Logger:
    return logging.getLogger(name)


def get_nonce() -> str:
    """Generate random 12 hexadecimal string

    :return: 12 hexadecimal char long string
    """
    return uuid.uuid4().hex[:12]


def get_ip(request: types.HttpRequest) -> str:
    if ip := request.headers.get("X-Real-IP"):
        return ip
    if ip := request.headers.get("X-Forwarded-For"):
        return ip
    return request.META.get("REMOTE_ADDR") or "255.255.255.255"
