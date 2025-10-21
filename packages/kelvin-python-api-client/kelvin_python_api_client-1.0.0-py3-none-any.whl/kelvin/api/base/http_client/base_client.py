"""
Kelvin API Client.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from types import TracebackType
from typing import (
    IO,
    TYPE_CHECKING,
    Callable,
    Optional,
    TypeVar,
    Union,
)
from urllib.parse import urlparse

import httpx
import structlog
from httpx import Response as Response
from pydantic import AnyUrl
from typing_extensions import override

from kelvin.api import version
from kelvin.api.base.error import ClientError
from kelvin.api.base.http_tools import RequestHistory, ResponseHistory

from .auth import (
    AsyncAuthConnection,
    AsyncAuthMiddleware,
    SyncAuthConnection,
    SyncAuthMiddleware,
)
from .env_vars import EnvVars
from .metadata import AsyncMetadata, SyncMetadata
from .retry import AsyncRetryTransport, RetryTransport

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter  # pragma: no cover

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)  # type: ignore[any]

FileContent = Union[IO[bytes], bytes, str]
FileTypes = Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    tuple[Optional[str], FileContent],
    # (filename, file (or bytes), content_type)
    tuple[Optional[str], FileContent, Optional[str]],
    # (filename, file (or bytes), content_type, headers)
    tuple[Optional[str], FileContent, Optional[str], Mapping[str, str]],
]
RequestFiles = Union[Mapping[str, FileTypes], Sequence[tuple[str, FileTypes]]]

PrimitiveData = Optional[Union[str, int, float, bool]]
QueryParamTypes = Union[
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    list[tuple[str, PrimitiveData]],
    tuple[tuple[str, PrimitiveData], ...],
    str,
    bytes,
]


class BaseClient:
    T = TypeVar("T", bound="BaseClient")  # type: ignore[any]
    USER_AGENT: str = f"kelvin-api-client=={version}"
    KELVIN_CLIENT: str = "kelvin-client"

    def __init__(
        self,
        *,
        url: Optional[AnyUrl],
        username: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
        password: Optional[str],
        totp: Optional[int],
        retries: Optional[int],
        timeout: Optional[Union[float, tuple[float, float]]],
        verbose: Optional[bool],
        plugins: Optional[list[Union[RequestHistory, ResponseHistory, object]]],  # object is here for linter purposes
    ) -> None:
        _env = EnvVars().KELVIN_CLIENT

        # logger.debug("Initializing BaseClient", env_vars=_env)

        url_item = url or _env.URL
        timeout_item = timeout or _env.TIMEOUT

        self.netloc: str = get_hostname(url_item)
        self.base_url: str = f"https://{self.netloc}"
        self.username: Optional[str] = username or _env.USERNAME
        self.password: Optional[str] = password or _env.PASSWORD
        self.client_id: str = client_id or _env.CLIENT_ID or self.KELVIN_CLIENT
        self.client_secret: Optional[str] = client_secret or _env.CLIENT_SECRET
        self.totp: Optional[int] = totp or _env.TOTP
        self.retries: int = retries or _env.RETRIES
        self.verbose: bool = verbose or False

        if isinstance(timeout_item, (int, float)):
            self.timeout: httpx.Timeout = httpx.Timeout(timeout_item)
        else:
            tmt, conn = timeout_item
            self.timeout = httpx.Timeout(tmt, connect=conn)

        # Event hooks for verbose logging
        self.event_hooks: Optional[Mapping[str, list[Callable[..., object]]]] = {"request": [], "response": []}
        self.async_event_hooks: Optional[Mapping[str, list[Callable[..., object]]]] = {"request": [], "response": []}

        if self.verbose:
            self.event_hooks["request"].append(self._log_request)
            self.async_event_hooks["request"].append(self._async_log_request)
            self.event_hooks["response"].append(self._log_response)
            self.async_event_hooks["response"].append(self._async_log_response)

        if plugins:
            for plugin in plugins:
                if isinstance(plugin, ResponseHistory):
                    self.event_hooks["response"].append(plugin.append)
                    self.async_event_hooks["response"].append(plugin.async_append)
                elif isinstance(plugin, RequestHistory):
                    self.event_hooks["request"].append(plugin.append)
                    self.async_event_hooks["request"].append(plugin.async_append)

        if len(self.event_hooks["request"]) == 0 and len(self.event_hooks["response"]) == 0:
            self.event_hooks = None
            self.async_event_hooks = None

        # Build headers
        self.headers: dict[str, str] = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json",
        }

    def _login(
        self,
        *,
        password: Optional[str] = None,
        totp: Optional[int] = None,
        client_secret: Optional[str] = None,
    ) -> None:
        self.password = password or self.password
        self.totp = totp or self.totp
        self.client_secret = client_secret or self.client_secret

    def _prepare_request(
        self,
        path: str,
        method: str,
        headers: Optional[Mapping[str, str]],
        timeout: Optional[Union[tuple[float, float], float]],
    ) -> tuple[str, str, dict[str, str], httpx.Timeout]:
        method = method.upper()

        headers = {**headers} if headers is not None else {}

        if timeout is None:
            local_timeout = self.timeout
        elif isinstance(timeout, (int, float)):
            local_timeout = httpx.Timeout(timeout)
        else:
            tmt, conn = timeout
            local_timeout = httpx.Timeout(tmt, connect=conn)

        return path, method, headers, local_timeout

    @override
    def __str__(self) -> str:
        """Return str(self)."""

        name = type(self).__name__

        return f"{name}(url={self.netloc!r})"

    @override
    def __repr__(self) -> str:
        """Return repr(self)."""

        return str(self)

    def _repr_pretty_(self, p: RepresentationPrinter, _: bool) -> None:
        """Pretty representation."""

        name = type(self).__name__

        with p.group(4, f"{name}(", ")"):
            p.text(f"url={self.netloc!r}")  # type: ignore[any]

    def _log_request(self, request: httpx.Request) -> None:
        try:
            body: Optional[str] = None
            if request.content:
                # Avoid dumping binary; cap length for safety
                body = request.content.decode()
                if len(body) > 1000:
                    body = body[:1000] + "...(truncated)"
            logger.info(request.__repr__(), headers=request.headers, body=body)
        except Exception as e:
            logger.error(f"Error logging request: {e}")

    async def _async_log_request(self, request: httpx.Request) -> None:
        self._log_request(request)

    def _log_response(self, response: httpx.Response) -> None:
        try:
            logger.info(
                response.__repr__(),
                url=response.request.url,
                headers=response.headers,
            )
        except Exception as e:
            logger.error(f"Error logging response: {e}")

    async def _async_log_response(self, response: httpx.Response) -> None:
        self._log_response(response)


class AsyncBaseClient(BaseClient):
    """
    Async base client
    """

    def __init__(
        self,
        *,
        url: Optional[AnyUrl] = None,
        username: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[int] = None,
        retries: Optional[int] = None,
        timeout: Optional[Union[float, tuple[float, float]]] = None,
        verbose: Optional[bool] = None,
        plugins: Optional[list[Union[RequestHistory, ResponseHistory, object]]] = None,
    ) -> None:
        super().__init__(
            url=url,
            username=username,
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            totp=totp,
            retries=retries,
            timeout=timeout,
            verbose=verbose,
            plugins=plugins,
        )

        self._client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            event_hooks=self.async_event_hooks,
            transport=AsyncRetryTransport(
                http2=True,
                retries=self.retries,
                limits=httpx.Limits(
                    max_keepalive_connections=50,
                    max_connections=50,
                ),
            ),
        )

        self._auth_conn: AsyncAuthConnection = AsyncAuthConnection(
            metadata=AsyncMetadata(self._client),
            client_id=self.client_id,
            username=self.username,
            password=self.password,
            totp=self.totp,
            client_secret=self.client_secret,
        )

    async def login(
        self,
        *,
        password: Optional[str] = None,
        totp: Optional[int] = None,
        client_secret: Optional[str] = None,
    ) -> None:
        if self._client.is_closed:
            raise ClientError("Cannot make request: client has been closed")

        super()._login(password=password, totp=totp, client_secret=client_secret)

        await self._auth_conn.login(
            username=self.username,
            password=self.password,
            totp=self.totp,
            client_secret=self.client_secret,
        )

    async def logout(self) -> None:
        await self._auth_conn.logout()
        await self.close()

    async def request(
        self,
        path: str,
        method: str,
        data: Optional[object] = None,
        params: Optional[QueryParamTypes] = None,
        files: Optional[RequestFiles] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[Union[tuple[float, float], float]] = None,
        stream: bool = False,
    ) -> Response:
        if self._client.is_closed:
            raise ClientError("Cannot make request: client has been closed")

        path, method, headers, local_timeout = self._prepare_request(path, method, headers, timeout)

        if stream:
            br = self._client.build_request(
                method,
                path,
                json=data,
                params=params,
                files=files,
                headers=headers,
                timeout=local_timeout,
            )
            return await self._client.send(
                br,
                follow_redirects=False,
                auth=AsyncAuthMiddleware(self._auth_conn),
                stream=True,
            )
        else:
            return await self._client.request(
                method,
                path,
                json=data,
                params=params,
                files=files,
                headers=headers,
                timeout=local_timeout,
                follow_redirects=False,
                auth=AsyncAuthMiddleware(self._auth_conn),
            )

    # -------------------------
    # Context management / close
    # -------------------------
    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncBaseClient:
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None = None,
        _exc_value: BaseException | None = None,
        _traceback: TracebackType | None = None,
    ) -> None:
        await self.close()


class SyncBaseClient(BaseClient):
    """
    Sync base client
    """

    def __init__(
        self,
        *,
        url: Optional[AnyUrl] = None,
        username: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        password: Optional[str] = None,
        totp: Optional[int] = None,
        retries: Optional[int] = None,
        timeout: Optional[Union[float, tuple[float, float]]] = None,
        verbose: Optional[bool] = None,
        plugins: Optional[list[Union[RequestHistory, ResponseHistory, object]]] = None,
    ) -> None:
        super().__init__(
            url=url,
            username=username,
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            totp=totp,
            retries=retries,
            timeout=timeout,
            verbose=verbose,
            plugins=plugins,
        )

        self._client: httpx.Client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            event_hooks=self.event_hooks,
            transport=RetryTransport(
                http2=True,
                retries=self.retries,
                limits=httpx.Limits(
                    max_keepalive_connections=50,
                    max_connections=50,
                ),
            ),
        )

        self._auth_conn: SyncAuthConnection = SyncAuthConnection(
            metadata=SyncMetadata(self._client),
            client_id=self.client_id,
            username=self.username,
            password=self.password,
            totp=self.totp,
            client_secret=self.client_secret,
        )

    def login(
        self,
        *,
        password: Optional[str] = None,
        totp: Optional[int] = None,
        client_secret: Optional[str] = None,
    ) -> None:
        if self._client.is_closed:
            raise ClientError("Cannot make request: client has been closed")

        super()._login(password=password, totp=totp, client_secret=client_secret)

        self._auth_conn.login(
            username=self.username,
            password=self.password,
            totp=self.totp,
            client_secret=self.client_secret,
        )

    def logout(self) -> None:
        self._auth_conn.logout()
        self.close()

    def request(
        self,
        path: str,
        method: str,
        data: Optional[object] = None,
        params: Optional[QueryParamTypes] = None,
        files: Optional[RequestFiles] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[Union[tuple[float, float], float]] = None,
        stream: bool = False,
    ) -> Response:
        if self._client.is_closed:
            raise ClientError("Cannot make request: client has been closed")

        path, method, headers, local_timeout = self._prepare_request(path, method, headers, timeout)

        if stream:
            br = self._client.build_request(
                method,
                path,
                json=data,
                params=params,
                files=files,
                headers=headers,
                timeout=local_timeout,
            )
            return self._client.send(
                br,
                follow_redirects=False,
                auth=SyncAuthMiddleware(self._auth_conn),
                stream=True,
            )
        else:
            return self._client.request(
                method,
                path,
                json=data,
                params=params,
                files=files,
                headers=headers,
                timeout=local_timeout,
                follow_redirects=False,
                auth=SyncAuthMiddleware(self._auth_conn),
            )

    # -------------------------
    # Context management / close
    # -------------------------
    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SyncBaseClient:
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None = None,
        _exc_value: BaseException | None = None,
        _traceback: TracebackType | None = None,
    ) -> None:
        self.close()


# -------------------------
# Utilities
# -------------------------

_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")


def get_hostname(url: Optional[AnyUrl]) -> str:
    if url is None:
        raise ValueError("missing url")

    value = str(url).strip().lower()

    # If no scheme, fallback to path
    # (AnyUrl should reject an empty scheme, but this is python, so...)
    if _SCHEME_RE.match(value) or value.startswith("//"):
        parsed = urlparse(value)
    else:
        parsed = urlparse(f"//{value}")

    result = parsed.hostname

    if not result:
        raise ValueError("url has invalid format")

    return result
