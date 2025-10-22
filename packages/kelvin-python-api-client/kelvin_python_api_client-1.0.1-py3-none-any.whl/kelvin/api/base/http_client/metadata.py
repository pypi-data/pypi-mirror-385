import asyncio
import threading
from _thread import LockType
from asyncio.locks import Lock

import httpx
from httpx._client import AsyncClient, Client
from httpx._models import Response

from kelvin.api.base.error import ClientError


class Metadata:
    _metadata_path: str = "/metadata"

    def __init__(self) -> None:
        self._json_metadata: dict[str, dict[str, str]] = {}
        self.realm: str = ""
        self.url: str = ""
        self.path: str = ""
        self.logout_path: str = ""

    def _store(self, json: object) -> None:
        auth_key = "authentication"
        try:
            if isinstance(json, dict):
                self._json_metadata = json
                self.realm = self._json_metadata[auth_key]["realm"]
                self.url = self._json_metadata[auth_key]["url"]
                self.path = self._json_metadata[auth_key]["path"]
                self.logout_path = self._json_metadata[auth_key]["logout_path"]
            else:
                raise ClientError("Invalid metadata format")
        except KeyError as e:
            raise ClientError(f"Missing key in metadata: {e}")


class AsyncMetadata(Metadata):
    def __init__(self, client: httpx.AsyncClient) -> None:
        super().__init__()
        self._client: AsyncClient = client
        self._lock: Lock = asyncio.Lock()

    async def fetch(self) -> None:
        async with self._lock:
            try:
                r: Response = await self._client.get(url=self._metadata_path)
                _ = r.raise_for_status()
                _json_metadata: object = r.json()  # type: ignore[any]
            except httpx.HTTPError:
                raise ClientError("Failed to retrieve metadata")
            self._store(json=_json_metadata)


class SyncMetadata(Metadata):
    def __init__(self, client: httpx.Client) -> None:
        super().__init__()
        self._client: Client = client
        self._lock: LockType = threading.Lock()

    def fetch(self) -> None:
        with self._lock:
            try:
                r: Response = self._client.get(url=self._metadata_path)
                _ = r.raise_for_status()
                _json_metadata: object = r.json()  # type: ignore[any]
            except httpx.HTTPError as e:
                raise ClientError(f"Failed to retrieve metadata: {e}") from e
            self._store(json=_json_metadata)
