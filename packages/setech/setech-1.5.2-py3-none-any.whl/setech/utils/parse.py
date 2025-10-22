import contextlib
import dataclasses
import datetime
import decimal
import json
import typing
import warnings

import httpx
import pydantic

from .warnings import deprecated as _deprecate

__all__ = [
    "SetechJSONEncoder",
    "as_decimal",
    "as_decimal_or_none",
    "jsonify_value",
    "shorten_value",
    "shortify_log_dict",
    "shortify_log_extra_data",
    "str_as_date",
    "str_as_date_or_none",
]


def as_decimal(decimal_str: str | float) -> decimal.Decimal:
    return decimal.Decimal(str(decimal_str))


def as_decimal_or_none(decimal_str: str | float | None) -> decimal.Decimal | None:
    if not isinstance(decimal_str, (str | int | float)):
        return None
    try:
        return as_decimal(decimal_str)
    except (decimal.DecimalException, TypeError):
        return None


def jsonify_value(value: typing.Any) -> typing.Any:
    """Return JSON'ified version of the object type-casted using SetechJSONEncoder

    :param value: any object
    :return: json compatible object
    """
    return json.loads(json.dumps(value, cls=SetechJSONEncoder))


class SetechJSONEncoder(json.JSONEncoder):
    def default(self, obj: typing.Any) -> typing.Any:
        try:
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            if isinstance(obj, datetime.datetime | datetime.date):
                return obj.isoformat()
            if isinstance(obj, pydantic.BaseModel):
                return obj.model_dump()
            if isinstance(obj, datetime.timedelta):
                return dict(__type__="timedelta", total_seconds=obj.total_seconds())
            if isinstance(obj, set):
                return sorted(obj, key=str)
            if isinstance(obj, httpx.Response):
                try:
                    content = obj.json()
                except json.JSONDecodeError:
                    content = obj.text
                return dict(
                    url=obj.url,
                    status_code=obj.status_code,
                    headers=sorted(obj.headers.multi_items(), key=lambda h: h[0]),
                    request=dict(
                        method=obj.request.method,
                        url=obj.request.url,
                        content=shorten_value(obj.request.content.decode("utf-8")),
                    ),
                    content=shorten_value(content),
                )
            if isinstance(obj, httpx.Request):
                try:
                    content = obj.content.decode("utf8")
                except UnicodeDecodeError:
                    content = obj.content
                with contextlib.suppress(json.JSONDecodeError):
                    content = json.loads(content)
                return dict(
                    method=obj.method,
                    url=obj.url,
                    headers=sorted(obj.headers.multi_items(), key=lambda h: h[0]),
                    content=shorten_value(content),
                )
            if hasattr(obj, "as_dict"):
                return obj.as_dict
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
                return dataclasses.asdict(obj)
            return super().default(obj)
        except TypeError as exc:
            if "not JSON serializable" in str(exc):
                return str(obj)
            raise exc  # pragma: no cover


def shorten_value(value: typing.Any) -> typing.Any:
    """Recursively shorten long string values and return a shortened version copy object.

    :param value: Object in which to recursively search for strings to shorten
    :return: Shortened version of the value
    """
    if isinstance(value, str):
        return f"{value[:30]}...{value[-30:]}" if isinstance(value, str) and len(value) > 64 else value  # noqa: PLR2004
    if isinstance(value, list):
        return [shorten_value(v) for v in value]
    if isinstance(value, tuple):
        return tuple(shorten_value(v) for v in value)
    if isinstance(value, dict):
        return {k: shorten_value(v) for k, v in value.items()}
    return value


def shortify_log_extra_data(log_value: typing.Any) -> dict[str, typing.Any]:
    """Shorten long values and normalize (to json compatible format) dictionary values

    :param log_value: Object to convert into json log favourable format
    :return: shortened and normalized object
    """
    shortened_log_value = shorten_value(jsonify_value(log_value))
    if not isinstance(shortened_log_value, dict):
        shortened_log_value = {"extra_data": shortened_log_value}
    return shortened_log_value


def str_as_date(date_str: str, date_format: str = "%Y-%m-%d") -> datetime.date:
    datetime_object = datetime.datetime.strptime(date_str, date_format)
    return datetime_object.date()


def str_as_date_or_none(date_str: str | None, date_format: str = "%Y-%m-%d") -> datetime.date | None:
    if not isinstance(date_str, str):
        return None
    try:
        return str_as_date(date_str, date_format)
    except (ValueError, TypeError):
        return None


@_deprecate(new_method=shortify_log_extra_data)
def shortify_log_dict(dct: typing.Any) -> dict[str, typing.Any]:
    warnings.warn("Deprecated method! Use `shortify_log_extra_data` instead", DeprecationWarning, 2)
    return shortify_log_extra_data(dct)
