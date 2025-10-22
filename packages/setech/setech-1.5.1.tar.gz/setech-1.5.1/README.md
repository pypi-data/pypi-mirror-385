# Example code
```python
# client.py
from setech import SyncClient


class LocalClient(SyncClient):
    name = "local"
    _base_url = "https://obligari.serveo.net/ping/local"

    def __init__(self, nonce=None):
        super().__init__(nonce)
        self._session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:123.0) Gecko/20100101 Firefox/123.0"}
        )

    def send_post_ping(self, var1: str, var2: int) -> bool:
        res = self.post("/some-post", json={"variable_one": var1, "second_variable": var2})
        return res.json().get("status")

    def send_put_ping(self, var1: str, var2: int) -> bool:
        res = self.put("/some-put", data={"variable_one": var1, "second_variable": var2})
        return res.json().get("status")

    def send_get_ping(self, var1: str, var2: int) -> bool:
        res = self.get("/some-get", params={"variable_one": var1, "second_variable": var2})
        return res.json().get("status")

    def send_patch_ping(self, var1: str, var2: int) -> bool:
        res = self.put("/some-patch", data=(("variable_one", var1), ("variable_one", var2)))
        return res.json().get("status")

    def send_trace_ping(self, var1: str, var2: int) -> bool:
        res = self.trace("/some-trace", params=(("variable_one", var1), ("variable_one", var2)))
        return res.json().get("status")
```

```python
# main.py
from .client import LocalClient


client = LocalClient()
client.send_post_ping("asd", 123)
client.send_put_ping("asd", 123)
client.send_get_ping("asd", 123)
client.send_patch_ping("asd", 123)
client.send_trace_ping("asd", 123)
```

## Log output
### Simple
```text
[14d709e02c0c] Preparing POST request to "https://obligari.serveo.net/ping/local/some-post"
[14d709e02c0c] Sending request with payload=b'{"variable_one": "asd", "second_variable": 123}'
[14d709e02c0c] Response response.status_code=200 str_repr_content='{"status":true,"request_id":62}'
[14d709e02c0c] Preparing GET request to "https://obligari.serveo.net/ping/local/some-get"
[14d709e02c0c] Sending request with payload=None
[14d709e02c0c] Response response.status_code=200 str_repr_content='{"status":true,"request_id":63}'
```
### Structured
```json
{"app": "dev", "level": "DEBUG", "name": "APIClient", "date_time": "2024-03-09 22:59:24", "location": "api_client/client.py:_request:71", "message": "[cfbdadc56f53] Preparing POST request to \"https://obligari.serveo.net/ping/local/some-post\"", "extra_data": {"hooks": {"response": []}, "method": "POST", "url": "https://obligari.serveo.net/ping/local/some-post", "headers": {}, "files": [], "data": [], "json": {"variable_one": "asd", "second_variable": 123}, "params": {}, "auth": null, "cookies": null}}
{"app": "dev", "level": "INFO", "name": "APIClient", "date_time": "2024-03-09 22:59:24", "location": "api_client/client.py:_request:74", "message": "[cfbdadc56f53] Sending request with payload=b'{\"variable_one\": \"asd\", \"second_variable\": 123}'", "extra_data": {"payload": "{\"variable_one\": \"asd\", \"second_variable\": 123}"}}
{"app": "dev", "level": "INFO", "name": "APIClient", "date_time": "2024-03-09 22:59:25", "location": "api_client/client.py:_request:81", "message": "[cfbdadc56f53] Response response.status_code=200 str_repr_content='{\"status\":true,\"request_id\":72}'", "extra_data": {"status_code": 200, "content": "{\"status\":true,\"request_id\":72}"}}
{"app": "dev", "level": "DEBUG", "name": "APIClient", "date_time": "2024-03-09 22:59:25", "location": "api_client/client.py:_request:71", "message": "[cfbdadc56f53] Preparing GET request to \"https://obligari.serveo.net/ping/local/some-get\"", "extra_data": {"hooks": {"response": []}, "method": "GET", "url": "https://obligari.serveo.net/ping/local/some-get", "headers": {}, "files": [], "data": [], "json": null, "params": {"variable_one": "asd", "second_variable": 123}, "auth": null, "cookies": null}}
{"app": "dev", "level": "INFO", "name": "APIClient", "date_time": "2024-03-09 22:59:25", "location": "api_client/client.py:_request:74", "message": "[cfbdadc56f53] Sending request with payload=None", "extra_data": {"payload": "{}"}}
{"app": "dev", "level": "INFO", "name": "APIClient", "date_time": "2024-03-09 22:59:25", "location": "api_client/client.py:_request:81", "message": "[cfbdadc56f53] Response response.status_code=200 str_repr_content='{\"status\":true,\"request_id\":74}'", "extra_data": {"status_code": 200, "content": "{\"status\":true,\"request_id\":73}"}}
```
