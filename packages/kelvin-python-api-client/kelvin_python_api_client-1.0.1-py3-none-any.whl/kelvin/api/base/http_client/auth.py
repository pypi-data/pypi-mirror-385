from __future__ import annotations

import asyncio
import threading
import typing
from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timedelta, timezone
from typing import cast

import httpx
import keycloak  # this lib should probably be replaced by an internal implementation
import keycloak.exceptions as kexceptions  # same as keycloak
import structlog
from typing_extensions import override

from kelvin.api.base.error import LoginError, LogoutError

from .metadata import AsyncMetadata, SyncMetadata

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)  # type: ignore[any]

TOKEN_LIFETIME_FRACTION = 0.9


class AuthConnection:
    def __init__(
        self,
        *,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        totp: typing.Optional[int] = None,
        client_secret: typing.Optional[str] = None,
        auth_code: typing.Optional[str] = None,
    ) -> None:
        self.username: typing.Optional[str] = username
        self.password: typing.Optional[str] = password
        self.totp: typing.Optional[int] = totp
        self.client_secret: typing.Optional[str] = client_secret
        self.auth_code: typing.Optional[str] = auth_code

        self._refresh_token: typing.Optional[str] = None
        self._access_token: typing.Optional[str] = None
        self._expires_at: typing.Optional[datetime] = None
        self._refresh_expires_at: typing.Optional[datetime] = None
        self._keycloak: typing.Optional[keycloak.KeycloakOpenID] = None

    def _set_auth_params(
        self,
        *,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        totp: typing.Optional[int] = None,
        client_secret: typing.Optional[str] = None,
        auth_code: typing.Optional[str] = None,
    ) -> None:
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        if totp is not None:
            self.totp = totp
        if client_secret is not None:
            self.client_secret = client_secret
        if auth_code is not None:
            self.auth_code = auth_code

    def _get_grant_type(
        self,
        *,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        client_secret: typing.Optional[str] = None,
        auth_code: typing.Optional[str] = None,
    ) -> str:
        if username is not None and password is not None:
            return "password"
        elif client_secret is not None:
            return "client_credentials"
        elif auth_code is not None:
            return "authorization_code"
        else:
            raise LoginError("Insufficient parameters for authentication.")

    def _clear_tokens(self) -> None:
        self._refresh_token = None
        self._access_token = None
        self._expires_at = None
        self._refresh_expires_at = None

    def _set_tokens(self, payload: object) -> str:
        self._clear_tokens()
        if isinstance(payload, dict):
            token: dict[str, object] = cast(dict[str, object], payload)
            if ("refresh_token" in token and isinstance(token["refresh_token"], str)) and (
                "refresh_expires_in" in token and isinstance(token["refresh_expires_in"], int)
            ):
                self._refresh_token = token["refresh_token"]
                self._refresh_expires_at = datetime.now(tz=timezone.utc) + timedelta(
                    seconds=int(TOKEN_LIFETIME_FRACTION * token["refresh_expires_in"]) or 0,
                )

            if ("access_token" in token and isinstance(token["access_token"], str)) and (
                "expires_in" in token and isinstance(token["expires_in"], int)
            ):
                self._access_token = token["access_token"]
                self._expires_at = datetime.now(tz=timezone.utc) + timedelta(
                    seconds=int(TOKEN_LIFETIME_FRACTION * token["expires_in"]) or 0,
                )

                return token["access_token"]

        raise LoginError("Failed to retrieve tokens")


class SyncAuthConnection(AuthConnection):
    def __init__(
        self,
        *,
        metadata: SyncMetadata,
        client_id: str,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        totp: typing.Optional[int] = None,
        client_secret: typing.Optional[str] = None,
        auth_code: typing.Optional[str] = None,
    ) -> None:
        super().__init__(
            username=username,
            password=password,
            totp=totp,
            client_secret=client_secret,
            auth_code=auth_code,
        )
        self._lock: threading.Lock = threading.Lock()
        self._metadata: SyncMetadata = metadata
        self.client_id: str = client_id

    def _unsafe_logout(self) -> None:
        if self._refresh_token is not None:
            token = self._refresh_token
            self._clear_tokens()
            if self._keycloak is not None:
                logout_url = f"{self._metadata.url}/{self._metadata.path}/realms/{self._metadata.realm}/logout"
                payload: dict[str, str] = {"client_id": self.client_id, "refresh_token": token}
                payload = self._keycloak._add_secret_key(payload)  # type: ignore[any]
                data_raw = self._keycloak.connection.raw_post(logout_url, data=payload)  # type: ignore[any]
                if data_raw.status_code != kexceptions.HTTP_NO_CONTENT:
                    raise LogoutError("Unable to logout")

    def logout(self) -> None:
        with self._lock:
            self._unsafe_logout()

    def _unsafe_login(self) -> str:
        if self._keycloak is None:
            self._metadata.fetch()
            self._keycloak: typing.Optional[keycloak.KeycloakOpenID] = keycloak.KeycloakOpenID(
                server_url=f"{self._metadata.url}/{self._metadata.path}/",
                realm_name=self._metadata.realm,
                client_id=self.client_id,
                client_secret_key=self.client_secret,
            )
        grant_type = self._get_grant_type(
            username=self.username,
            password=self.password,
            client_secret=self.client_secret,
            auth_code=self.auth_code,
        )
        try:
            token = self._keycloak.token(  # type: ignore[any]
                grant_type=grant_type,
                username=self.username or "",
                password=self.password or "",
                totp=self.totp,
                code=self.auth_code or "",
            )
        except keycloak.KeycloakAuthenticationError:
            raise LoginError("Incorrect credentials")
        return self._set_tokens(payload=token)  # type: ignore[any]

    def login(
        self,
        *,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        totp: typing.Optional[int] = None,
        client_secret: typing.Optional[str] = None,
        auth_code: typing.Optional[str] = None,
    ) -> None:
        with self._lock:
            self._set_auth_params(
                username=username,
                password=password,
                totp=totp,
                client_secret=client_secret,
                auth_code=auth_code,
            )
            _ = self._unsafe_login()

    def get_access_token(self) -> str:
        with self._lock:
            if (
                self._keycloak is None
                or self._access_token is None
                or self._expires_at is None
                or self._refresh_token is None
                or self._refresh_expires_at is None
            ):
                return self._unsafe_login()
            elif datetime.now(tz=timezone.utc) < self._expires_at:
                return self._access_token
            elif datetime.now(tz=timezone.utc) >= self._refresh_expires_at:
                try:
                    self._unsafe_logout()
                except LogoutError as e:
                    logger.debug("Logout error", exc_info=e)
                return self._unsafe_login()
            else:
                try:
                    token = self._keycloak.refresh_token(  # type: ignore[any]
                        refresh_token=self._refresh_token,
                    )
                except keycloak.KeycloakAuthenticationError:
                    self._clear_tokens()
                    raise LoginError("Failed to refresh token.")
                self._set_tokens(payload=token)  # type: ignore[any]
                return self._access_token


class AsyncAuthConnection(AuthConnection):
    def __init__(
        self,
        metadata: AsyncMetadata,
        client_id: str,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        totp: typing.Optional[int] = None,
        client_secret: typing.Optional[str] = None,
        auth_code: typing.Optional[str] = None,
    ) -> None:
        super().__init__(
            username=username,
            password=password,
            totp=totp,
            client_secret=client_secret,
            auth_code=auth_code,
        )
        self._lock: asyncio.Lock = asyncio.Lock()
        self._metadata: AsyncMetadata = metadata
        self.client_id: str = client_id

    async def _unsafe_logout(self) -> None:
        if self._refresh_token is not None:
            token = self._refresh_token
            self._clear_tokens()
            if self._keycloak is not None:
                logout_url = f"{self._metadata.url}/{self._metadata.path}/realms/{self._metadata.realm}/logout"
                payload: dict[str, str] = {"client_id": self.client_id, "refresh_token": token}
                payload = self._keycloak._add_secret_key(payload)  # type: ignore[any]
                data_raw = await self._keycloak.connection.a_raw_post(logout_url, data=payload)  # type: ignore[any]
                if data_raw.status_code != kexceptions.HTTP_NO_CONTENT:
                    raise LogoutError("Unable to logout")

    async def logout(self) -> None:
        async with self._lock:
            await self._unsafe_logout()

    async def _unsafe_login(self) -> str:
        if self._keycloak is None:
            await self._metadata.fetch()
            self._keycloak: typing.Optional[keycloak.KeycloakOpenID] = keycloak.KeycloakOpenID(
                server_url=f"{self._metadata.url}/{self._metadata.path}/",
                realm_name=self._metadata.realm,
                client_id=self.client_id,
                client_secret_key=self.client_secret,
            )
        grant_type = self._get_grant_type(
            username=self.username,
            password=self.password,
            client_secret=self.client_secret,
            auth_code=self.auth_code,
        )
        try:
            token = await self._keycloak.a_token(  # type: ignore[any]
                grant_type=grant_type,
                username=self.username or "",
                password=self.password or "",
                totp=self.totp,
                code=self.auth_code or "",
            )
        except keycloak.KeycloakAuthenticationError:
            raise LoginError("Incorrect credentials")
        return self._set_tokens(payload=token)  # type: ignore[any]

    async def login(
        self,
        *,
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        totp: typing.Optional[int] = None,
        client_secret: typing.Optional[str] = None,
        auth_code: typing.Optional[str] = None,
    ) -> None:
        async with self._lock:
            self._set_auth_params(
                username=username,
                password=password,
                totp=totp,
                client_secret=client_secret,
                auth_code=auth_code,
            )
            _ = await self._unsafe_login()

    async def get_access_token(self) -> str:
        async with self._lock:
            if (
                self._keycloak is None
                or self._access_token is None
                or self._expires_at is None
                or self._refresh_token is None
                or self._refresh_expires_at is None
            ):
                return await self._unsafe_login()
            elif datetime.now(tz=timezone.utc) < self._expires_at:
                return self._access_token
            elif datetime.now(tz=timezone.utc) >= self._refresh_expires_at:
                try:
                    await self._unsafe_logout()
                except LogoutError as e:
                    logger.debug("Logout error", exc_info=e)
                return await self._unsafe_login()
            else:
                try:
                    token = await self._keycloak.a_refresh_token(  # type: ignore[any]
                        refresh_token=self._refresh_token,
                    )
                except keycloak.KeycloakAuthenticationError:
                    self._clear_tokens()
                    raise LoginError("Failed to refresh token.")
                self._set_tokens(payload=token)  # type: ignore[any]
                return self._access_token


class SyncAuthMiddleware(httpx.Auth):
    """
    Implements httpx auth.
    """

    def __init__(self, conn: SyncAuthConnection) -> None:
        self._conn: SyncAuthConnection = conn

    @override
    def sync_auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        token = self._conn.get_access_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request


class AsyncAuthMiddleware(httpx.Auth):
    """
    Implements httpx auth.
    """

    def __init__(self, conn: AsyncAuthConnection) -> None:
        self._conn: AsyncAuthConnection = conn

    @override
    async def async_auth_flow(self, request: httpx.Request) -> AsyncGenerator[httpx.Request, httpx.Response]:
        token = await self._conn.get_access_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request
