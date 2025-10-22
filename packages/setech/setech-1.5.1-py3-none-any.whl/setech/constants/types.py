import typing
from collections import abc


class HttpRequest:
    """Data struct stub to mimic django.http.HttpRequest object"""

    headers: abc.Mapping[str, str]
    META: dict[str, typing.Any]
