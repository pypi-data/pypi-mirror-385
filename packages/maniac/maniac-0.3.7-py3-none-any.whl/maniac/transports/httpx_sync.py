# maniac/transports/httpx_sync.py
import httpx, json, ssl, certifi
from typing import Any, Dict, Iterable, Optional


class HttpxTransport:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self.client = httpx.Client(verify=certifi.where(), http2=True, timeout=60)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "HttpxTransport":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    @staticmethod
    def headers(
        api_key: Optional[str] = None, extra: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        return {
            "content-type": "application/json",
            "maniac-apikey": api_key or "",
            **(extra or {}),
        }

    def request_json(
        self,
        path: str,
        init: Dict[str, Any],
    ) -> Any:
        url = f"{self._base_url}{path}"
        r = self.client.request(
            init.get("method", "GET"),
            url,
            headers=init.get("headers"),
            content=init.get("body"),
        )
        r.raise_for_status()
        return r.json()

    def sse_events(self, path: str, payload: Any):
        url = f"{self._base_url}{path}"
        init = {
            "method": "POST",
            "headers": self.headers(
                self._api_key, extra={"Accept": "text/event-stream"}
            ),
            "body": json.dumps(payload),
        }
        with self.client.stream(
            "POST", url, headers=init["headers"], content=init["body"]
        ) as r:
            r.raise_for_status()
            # Basic SSE line parser
            buf = ""
            for chunk in r.iter_text():
                if not chunk:
                    continue
                buf += chunk
                while "\n\n" in buf:
                    raw, buf = buf.split("\n\n", 1)
                    for line in raw.splitlines():
                        if not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if not data or data == "[DONE]":
                            if data == "[DONE]":
                                return
                            continue
                        try:
                            yield json.loads(data)
                        except Exception:
                            continue
