"""
Custom Retrier.
"""

from __future__ import annotations

import asyncio
import random
import ssl
import time
from collections.abc import Iterable, Iterator
from http import HTTPStatus
from typing import Final, Optional

import httpx
from httpx._config import DEFAULT_LIMITS
from httpx._transports.default import SOCKET_OPTION
from httpx._types import CertTypes, ProxyTypes
from typing_extensions import override

RETRIES_BACKOFF_FACTOR: Final[float] = 0.5
RETRIES_MAX_BACKOFF: Final[float] = 60.0
RETRIES_JITTER_FACTOR: Final[float] = 1.0
RETRIES_MAX: Final[int] = 10

RETRYABLE_STATUS_CODES: Final[frozenset[HTTPStatus]] = frozenset(
    [
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    ]
)

RETRYABLE_EXCEPTIONS: Final[tuple[type[httpx.HTTPError], ...]] = (
    httpx.TimeoutException,
    httpx.NetworkError,
    httpx.RemoteProtocolError,
)

systemrandom: random.SystemRandom = random.SystemRandom()


def exponential_backoff(factor: float, max_backoff: float, jitter: float) -> Iterator[float]:
    """
    Yields successive backoff delays (seconds).
    First value is the first *post-failure* delay.
    """
    n = 0.0
    while True:
        if factor <= 0:
            yield 0.0
        else:
            base = min(factor * (2**n), max_backoff)
            if jitter <= 0:
                delay = base
            elif jitter >= 1.0:
                # full jitter: [0, base]
                delay = systemrandom.uniform(0, base)
            else:
                # partial jitter: [(1-j)*base, base]
                delay = base * systemrandom.uniform(1 - jitter, 1)
            yield delay
        n += 1


def parse_retry_after(value: str) -> Optional[float]:
    # RFC 7231: either delta-seconds or HTTP-date. We support delta-seconds.
    try:
        secs = float(value.strip())
        return max(0.0, secs)
    except Exception:
        return None


class RetryTransport(httpx.HTTPTransport):
    def __init__(
        self,
        *,
        verify: ssl.SSLContext | str | bool = True,
        cert: CertTypes | None = None,
        trust_env: bool = True,
        http1: bool = True,
        http2: bool = False,
        limits: httpx.Limits = DEFAULT_LIMITS,
        proxy: ProxyTypes | None = None,
        uds: str | None = None,
        local_address: str | None = None,
        retries: int = 0,
        socket_options: Iterable[SOCKET_OPTION] | None = None,
    ) -> None:
        if retries < 0:
            raise ValueError("retries must be non-negative")
        if retries > RETRIES_MAX:
            raise ValueError(f"retries must not exceed {RETRIES_MAX}")
        self._retries: int = retries

        super().__init__(
            verify=verify,
            cert=cert,
            trust_env=trust_env,
            http1=http1,
            http2=http2,
            limits=limits,
            proxy=proxy,
            uds=uds,
            local_address=local_address,
            retries=0,
            socket_options=socket_options,
        )

    @override
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        tries: int = 0
        delays = exponential_backoff(RETRIES_BACKOFF_FACTOR, RETRIES_MAX_BACKOFF, RETRIES_JITTER_FACTOR)
        retry_after: Optional[float] = None

        while True:
            try:
                response = super().handle_request(request)

                if HTTPStatus(response.status_code) not in RETRYABLE_STATUS_CODES:
                    return response

                if tries >= self._retries:
                    return response

                retry_after_header = response.headers.get("Retry-After")  # type: ignore[any]
                if retry_after_header and isinstance(retry_after_header, str):
                    retry_after = parse_retry_after(retry_after_header)

                # close the response before retrying
                response.close()

            except Exception as e:
                if not isinstance(e, RETRYABLE_EXCEPTIONS):
                    raise

                if tries >= self._retries:
                    raise

            tries += 1
            delay: float = retry_after or next(delays)
            if delay > 0:
                time.sleep(delay)


class AsyncRetryTransport(httpx.AsyncHTTPTransport):
    def __init__(
        self,
        *,
        verify: ssl.SSLContext | str | bool = True,
        cert: CertTypes | None = None,
        trust_env: bool = True,
        http1: bool = True,
        http2: bool = False,
        limits: httpx.Limits = DEFAULT_LIMITS,
        proxy: ProxyTypes | None = None,
        uds: str | None = None,
        local_address: str | None = None,
        retries: int = 0,
        socket_options: Iterable[SOCKET_OPTION] | None = None,
    ) -> None:
        if retries < 0:
            raise ValueError("retries must be non-negative")
        if retries > RETRIES_MAX:
            raise ValueError(f"retries must not exceed {RETRIES_MAX}")
        self._retries: int = retries

        super().__init__(
            verify=verify,
            cert=cert,
            trust_env=trust_env,
            http1=http1,
            http2=http2,
            limits=limits,
            proxy=proxy,
            uds=uds,
            local_address=local_address,
            retries=0,
            socket_options=socket_options,
        )

    @override
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        tries: int = 0
        delays = exponential_backoff(RETRIES_BACKOFF_FACTOR, RETRIES_MAX_BACKOFF, RETRIES_JITTER_FACTOR)
        retry_after: Optional[float] = None

        while True:
            try:
                response = await super().handle_async_request(request)

                if HTTPStatus(response.status_code) not in RETRYABLE_STATUS_CODES:
                    return response

                if tries >= self._retries:
                    return response

                retry_after_header = response.headers.get("Retry-After")  # type: ignore[any]
                if retry_after_header and isinstance(retry_after_header, str):
                    retry_after = parse_retry_after(retry_after_header)

                # close the response before retrying
                await response.aclose()

            except Exception as e:
                if not isinstance(e, RETRYABLE_EXCEPTIONS):
                    raise

                if tries >= self._retries:
                    raise

            tries += 1
            delay: float = retry_after or next(delays)
            if delay > 0:
                await asyncio.sleep(delay)
