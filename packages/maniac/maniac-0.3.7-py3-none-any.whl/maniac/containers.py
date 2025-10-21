from maniac.client import Maniac
from typing import Any, Dict, Iterable, Optional, List
from .transports.httpx_sync import HttpxTransport
from .types import (
    ChatCompletion,
    ChatCompletionCreateParams,
    ChatCompletionChunk,
    ContainerCreateParams,
    Container,
    RegisterCompletionsParams,
    RegisterCompletionsSuccess,
)

import os
import json
import io
import tarfile
import hashlib
import inspect
import importlib

try:
    import cloudpickle
except Exception as _e:
    cloudpickle = None


from dataclasses import dataclass


class _Containers:
    def __init__(self, p: "Maniac"):
        self._p = p

    def create(self, params: ContainerCreateParams) -> Container:
        """
        Create a new container. Uses POST /v1/containers
        """
        body = json.dumps(params)
        res = self._p._tx.request_json(
            "/v1/containers",
            {"method": "POST", "headers": self._p._tx.headers(), "body": body},
        )
        return res.get("data")
