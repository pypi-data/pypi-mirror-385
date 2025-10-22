import base64
import logging
from logging import LogRecord
from logging.handlers import HTTPHandler
from typing import Any


class JSONHttpPostHandler(HTTPHandler):
    """
    A class which sends records to a web server, using POST semantics.
    """

    def __init__(self, host: str, url: str, secure: bool = False, credentials: Any = None, context: Any = None):
        """
        Initialize the instance with the host and the request URL
        """
        logging.Handler.__init__(self)
        if not secure and context is not None:
            raise ValueError("context parameter only makes sense with secure=True")
        self.host = host
        self.url = url
        self.method = "POST"
        self.secure = secure
        self.credentials = credentials
        self.context = context

    def emit(self, record: LogRecord) -> None:
        """
        Emit a record.

        Send the record to the web server as a JSON
        """
        try:
            host = self.host
            h = self.getConnection(host, self.secure)
            url = self.url
            data = self.format(record)
            h.putrequest(self.method, url)
            h.putheader("Content-type", "application/json")
            h.putheader("Content-length", str(len(data)))
            if self.credentials:
                _creds = base64.b64encode(("{}:{}".format(*self.credentials)).encode("utf-8")).strip().decode("utf-8")
                h.putheader("Authorization", f"Basic {_creds}")
            h.endheaders()
            self.format(record)
            h.send(data.encode("utf-8"))
            h.getresponse()  # can't do anything with the result
        except Exception:  # noqa: BLE001
            self.handleError(record)
