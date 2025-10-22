"""
API Service Model.
"""

from __future__ import annotations

import json
from collections import ChainMap
from collections.abc import AsyncGenerator, AsyncIterator, Iterator, Mapping, Sequence
from contextlib import AbstractAsyncContextManager, AbstractContextManager, AsyncExitStack, ExitStack
from datetime import datetime, timezone
from string import Formatter
from types import FunctionType, MethodType
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    TypeVar,
    Union,
    cast,
)
from urllib.parse import quote

import structlog
from pydantic import ConfigDict, ValidationError
from pydantic._internal._model_construction import ModelMetaclass
from pydantic.v1.utils import Obj
from typing_inspect import get_args, get_origin

from kelvin.api.client.model.pagination import PaginationLimits

from .base_model import BaseModel, BaseModelRoot
from .data_model import AsyncKIterator, DataModel, KIterator, KList
from .error import APIError, ResponseError
from .http_client.base_client import AsyncBaseClient, PrimitiveData, Response, SyncBaseClient
from .utils import guess_mime_type, metadata_tuple

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)  # type: ignore[any]

T = TypeVar("T")

JSON_CONTENT_TYPES = (
    "application/json",
    "application/x-json-stream",
)


def resolve_fields(x: Mapping[str, object]) -> Mapping[str, object]:
    """Resolve fields from data models."""

    result: dict[str, object] = {k: v for k, v in x.items() if v is not None}
    items = [*x.items()]

    for name, value in items:
        if "_" in name and isinstance(value, DataModel):
            head, tail = name.rsplit("_", 1)
            if head != type(value).__name__.lower():
                raise TypeError(f"Unable to get {name!r} from {type(value).__name__!r} object")
            value = result[name] = value[tail]
        if isinstance(value, datetime):
            suffix = "Z" if value.microsecond else ".000000Z"
            result[name] = value.astimezone(timezone.utc).replace(tzinfo=None).isoformat() + suffix
    return result


def primitive_data(x: object) -> PrimitiveData:
    if isinstance(x, str):
        return x
    elif isinstance(x, int):
        return x
    elif isinstance(x, float):
        return x
    elif isinstance(x, bool):
        return x
    else:
        try:
            return str(x)
        except Exception:
            logger.error(f"Unable to convert {x!r} to string", exc_info=True)
            return None


def query_param_payload(x: Mapping[str, object]) -> Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]]:
    result: dict[str, Union[PrimitiveData, Sequence[PrimitiveData]]] = {}

    for name, value in x.items():
        if isinstance(value, list):
            result[name] = [primitive_data(item) for item in value]  # type: ignore[any]
        else:
            result[name] = primitive_data(value)

    return result


def map_object_to_string(x: Mapping[str, object]) -> Mapping[str, str]:
    result: dict[str, str] = {}

    for name, value in x.items():
        if isinstance(value, str):
            result[name] = value
        elif isinstance(value, int):
            result[name] = str(value)
        elif isinstance(value, float):
            result[name] = str(value)
        elif isinstance(value, bool):
            result[name] = str(value)
        else:
            try:
                result[name] = str(value)
            except Exception:
                logger.error(f"Unable to convert {value!r} to string", exc_info=True)

    return result


def format_path(path: str, values: Mapping[str, object]) -> str:
    if "{" in path:
        procValues: dict[str, object] = {}
        path_vars = {fname for _, fname, _, _ in Formatter().parse(path) if fname}
        for fname in path_vars:
            value = values.get(fname)
            if isinstance(value, str):
                quoted_value = quote(value, safe="")
                procValues[fname] = quoted_value
            else:
                procValues[fname] = value
        path = path.format_map(procValues)
    return path


def prepare_files(
    files: Mapping[str, object],
) -> tuple[Mapping[str, tuple[str, Optional[str]]], Optional[tuple[str, tuple[None, str]]]]:
    metadata: Optional[tuple[str, tuple[None, str]]] = None
    returnFiles: dict[str, tuple[str, Optional[str]]] = {}

    for k, v in files.items():
        if k == "metadata":
            metadata = ("metadata", metadata_tuple(v))
        elif isinstance(v, str):
            returnFiles[k] = (v, guess_mime_type(v))
        else:
            raise TypeError(f"Invalid file type for key '{k}': {type(v)}")

    return returnFiles, metadata


def build_body_data(
    body_type: Optional[type[DataModel]],
    data: Optional[Union[Sequence[Mapping[str, object]], Mapping[str, object]]],
    array_body: bool,
    **kwargs: object,
) -> Optional[Union[list[dict[str, object]], dict[str, object]]]:
    if body_type is None:
        return None

    fields = body_type.model_fields

    def _dump_model(model_obj: DataModel) -> dict[str, object]:
        return model_obj.model_dump(mode="json", by_alias=True, exclude_none=True, exclude_unset=True)

    def prepare(x: Mapping[str, object]) -> dict[str, object]:
        merged = ChainMap(kwargs or {}, dict(x) if x else {})
        # keep only declared fields, drop Nones
        return {name: merged.get(name) for name in fields if merged.get(name) is not None}

    if array_body:
        seq: Sequence[Mapping[str, object]] = []
        if isinstance(data, Sequence):
            seq = data
        else:
            raise ValueError("Data must be a sequence of mappings")

        return [_dump_model(body_type(**prepare(x))) for x in seq]

    # single object
    mapping: Mapping[str, object] = {}
    if data:
        if isinstance(data, Mapping):
            mapping = data
        else:
            raise ValueError("Data must be a mapping")
    return _dump_model(body_type(**prepare(mapping)))


def process_converter(response: Response, result_types: Mapping[str, Optional[type[Any]]]) -> Callable[[Any], Any]:
    content_type = response.headers.get("Content-Type", "")
    status_code = response.status_code
    result_type = result_types.get(str(status_code))

    if str(status_code) not in result_types:
        logger.warning("Unexpected response code", status_code=status_code)
        if not response.is_success:
            # using dummy x: x to not change the APIError behavior
            raise APIError(response, lambda x: x)

    if isinstance(result_type, type):
        if not content_type.startswith(JSON_CONTENT_TYPES):
            raise ResponseError(
                f"Unexpected response for {result_type.__name__}",  # type: ignore
                response,
            )

        def converter(x: Any) -> Any:
            if issubclass(result_type, BaseModelRoot):  # type: ignore
                return result_type(x)  # type: ignore

            if isinstance(x, list):
                return result_type(x)  # type: ignore
            return result_type(**x)  # type: ignore

    elif get_origin(result_type) is list:
        result_type, *_ = get_args(result_type)
        if not content_type.startswith(JSON_CONTENT_TYPES):
            raise ResponseError(
                f"Unexpected response for {result_type.__name__}",  # type: ignore
                response,
            )

        def converter(x: Any) -> Any:
            return KList([result_type(**v) for v in x])  # type: ignore

    else:

        def converter(x: Any) -> Any:
            return x

    if not response.is_success:
        raise APIError(response, converter)

    return converter


def process_sync_edge_case_responses(response: Response) -> Optional[Union[Iterator[str], Iterator[bytes], str]]:
    content_type: str = response.headers.get("Content-Type", "")  # type: ignore[any]
    if content_type == "application/octet-stream":
        return response.iter_bytes(1024)

    elif content_type == "application/yaml":
        return response.iter_text(1024)

    elif not content_type.startswith(JSON_CONTENT_TYPES):
        return response.text

    return None


async def process_async_edge_case_responses(
    response: Response,
) -> Optional[Union[AsyncIterator[bytes], AsyncIterator[str]]]:
    content_type: str = response.headers.get("Content-Type", "")  # type: ignore[any]
    if content_type == "application/octet-stream":
        return response.aiter_bytes(1024)
    elif content_type == "application/yaml":
        return response.aiter_text(1024)
    elif not content_type.startswith(JSON_CONTENT_TYPES):

        async def wrapper_s() -> AsyncIterator[str]:
            yield response.text

        return wrapper_s()
    else:
        return None


class ApiServiceModelMeta(ModelMetaclass):
    """DataModel metaclass."""

    def __new__(
        metacls: type[ApiServiceModelMeta], name: str, bases: tuple[type, ...], __dict__: dict[str, Any]
    ) -> ApiServiceModelMeta:
        cls = cast(ApiServiceModelMeta, super().__new__(metacls, name, bases, __dict__))

        # kill unused fields so that they can be used by models
        cls.fields = cls.schema = None  # type: ignore

        return cls

    def __repr__(self) -> str:
        """Pretty representation."""

        methods = "\n".join(
            f"  - {name}: " + x.__doc__.lstrip().split("\n")[0]
            for name, x in ((name, getattr(self, name)) for name in sorted(vars(self)) if not name.startswith("_"))
            if x.__doc__ is not None and isinstance(x, (FunctionType, MethodType))
        )

        return f"{self.__name__}:\n{methods}"

    def __str__(self) -> str:
        """Return str(self)."""

        return f"<class {self.__name__!r}>"


P = TypeVar("P", bound=DataModel)


class ApiServiceModel(BaseModel, metaclass=ApiServiceModelMeta):
    """API Service Model base-class."""

    if TYPE_CHECKING:
        fields: Any = None
        schema: Any = None
    model_config: ConfigDict = ConfigDict(extra="allow")  # type: ignore[misc]  # this is currently being refactored

    def __getattribute__(self, name: str) -> Any:
        """Get attribute."""

        if name.startswith("_"):
            return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute."""

        if name.startswith("_"):
            super().__setattr__(name, value)

    @classmethod
    def _make_request(
        cls,
        client: Optional[SyncBaseClient],
        method: str,
        path: str,
        values: Mapping[str, object],
        params: Mapping[str, object],
        files: Mapping[str, object],
        headers: Mapping[str, object],
        data: Optional[Union[Mapping[str, object], Sequence[Mapping[str, object]]]],
        body_type: Optional[type[DataModel]],
        array_body: bool,
        result_types: Mapping[str, Optional[type[object]]],
        stream: bool = False,
        dry_run: bool = False,
        **kwargs: object,
    ) -> Any:
        """Make request to API."""

        if client is None:
            raise ValueError("No client set.")

        # check for fields that need to be dereferenced
        values = resolve_fields(values)
        params = resolve_fields(params)
        files = resolve_fields(files)
        headers = resolve_fields(headers)

        # normalize params and headers
        params = query_param_payload(params)
        headers = map_object_to_string(headers)

        path = format_path(path, values)

        body_data = build_body_data(body_type, data, array_body, **kwargs)

        files, metadata = prepare_files(files)

        if dry_run:
            return {
                "path": path,
                "method": method,
                "data": body_data,
                "params": params,
                "files": files,
                "headers": headers,
            }

        if len(files) > 0:
            with ExitStack() as stack:
                openFiles: list[tuple[str, Union[tuple[str, IO[bytes], Optional[str]], tuple[None, str]]]] = []
                for key, tup in files.items():
                    fname, mime_type = tup
                    openFile = stack.enter_context(open(fname, "rb"))
                    openFiles.append((key, (fname, openFile, mime_type)))
                if metadata:
                    openFiles.append(metadata)

                response = client.request(path, method, body_data, params, openFiles, headers, stream=stream)

        else:
            response = client.request(
                path=path, method=method, data=body_data, params=params, headers=headers, stream=stream
            )

        if not stream:
            pr = process_sync_edge_case_responses(response)
            if pr is not None:
                return pr

            converter = process_converter(response, result_types)

            try:
                return converter(response.json())
            except ValidationError as e:
                raise e from None

        else:
            return cls._iwrapper(response, result_types)

    @classmethod
    def _iwrapper(cls, resp: Response, result_types: Mapping[str, Optional[type[object]]]) -> Iterator[object]:
        pr = process_sync_edge_case_responses(resp)
        if pr is not None:

            def wrapper() -> Iterator[object]:
                try:
                    for record in pr:
                        yield record
                finally:
                    resp.close()

            return wrapper()

        else:

            def results() -> Iterator[Response]:
                i = -1
                errors = []
                success = False
                try:
                    converter = process_converter(resp, result_types)
                    for x in resp.iter_lines():
                        if not x:
                            continue
                        i += 0
                        records = json.loads(x)
                        if isinstance(records, dict):
                            records = [records]

                        for record in records:
                            try:
                                yield converter(record)
                            except ValidationError as e:
                                errors += [(i, e)]
                                continue
                            else:
                                success = True

                    if not errors:
                        return

                    if not success:
                        raise errors[0][1] from None
                    elif errors:
                        summary = "\n".join(f"  {i}: {x}" for i, x in errors)
                        logger.warning("Skipped items", summary=summary)
                finally:
                    resp.close()

            results.__qualname__ = "results"

            return KIterator(results())

    @classmethod
    def scan(
        cls,
        client: Optional[SyncBaseClient],
        path: str,
        api_response: Any,
        flatten: bool = True,
        method: str = "GET",
        data: Any = None,
    ) -> Iterator[Any]:
        """Iterate pages."""

        result = api_response

        if client is None:
            raise ValueError("No client set.")

        while True:
            if not result.data:
                return

            if flatten:
                yield from result.data
            else:
                yield result.data

            pagination = result.pagination
            if pagination is None:
                return

            if isinstance(pagination, PaginationLimits):
                page = pagination.page
                if page is None:
                    return

                total_pages = pagination.total_pages
                if page == total_pages:
                    return
                page_size = len(result.data)
                params = {"page": page + 1, "page_size": page_size}
            else:
                next_page = pagination.next_page
                if next_page is None:
                    return

                if "?" in next_page:
                    path = next_page
                    params = {}
                else:
                    page_size = len(result.data)
                    params = {"next": next_page, "page_size": page_size}

            responses = client.request(path, method=method, params=params, data=data)
            if isinstance(responses, Response):
                result = type(api_response)(**responses.json(), client=client)
            else:
                with responses as response:
                    for resp in response.iter_bytes():
                        yield type(api_response)(**json.loads(resp), client=client)

    @classmethod
    def fetch(
        cls, client: Optional[SyncBaseClient], path: str, api_response: Any, method: str = "GET", data: Any = None
    ) -> Sequence[Any]:
        """Fetch all data."""

        return type(api_response.data)(cls.scan(client, path, api_response, flatten=True, method=method, data=data))


class AsyncApiServiceModel(BaseModel, metaclass=ApiServiceModelMeta):
    """API Service Model base-class."""

    if TYPE_CHECKING:
        fields: Any = None
        schema: Any = None
    model_config: ConfigDict = ConfigDict(extra="allow")  # type: ignore[misc]  # this is currently being refactored

    def __getattribute__(self, name: str) -> Any:
        """Get attribute."""

        if name.startswith("_"):
            return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute."""

        if name.startswith("_"):
            super().__setattr__(name, value)

    @classmethod
    async def _make_request(
        cls,
        client: Optional[AsyncBaseClient],
        method: str,
        path: str,
        values: Mapping[str, object],
        params: Mapping[str, object],
        files: Mapping[str, object],
        headers: Mapping[str, object],
        data: Optional[Union[Mapping[str, object], Sequence[Mapping[str, object]]]],
        body_type: Optional[type[DataModel]],
        array_body: bool,
        result_types: Mapping[str, Optional[type[object]]],
        stream: bool = False,
        dry_run: bool = False,
        **kwargs: object,
    ) -> Any:
        """Make request to API."""

        if client is None:
            raise ValueError("No client set.")

        # check for fields that need to be dereferenced
        values = resolve_fields(values)
        params = resolve_fields(params)
        files = resolve_fields(files)
        headers = resolve_fields(headers)

        # normalize params and headers
        params = query_param_payload(params)
        headers = map_object_to_string(headers)

        path = format_path(path, values)

        body_data = build_body_data(body_type, data, array_body, **kwargs)

        files, metadata = prepare_files(files)

        if dry_run:
            return {
                "path": path,
                "method": method,
                "data": body_data,
                "params": params,
                "files": files,
                "headers": headers,
            }

        if len(files) > 0:
            async with AsyncExitStack() as stack:
                openFiles: list[tuple[str, Union[tuple[str, IO[bytes], Optional[str]], tuple[None, str]]]] = []
                for key, tup in files.items():
                    fname, mime_type = tup
                    openFile = stack.enter_context(open(fname, "rb"))
                    openFiles.append((key, (fname, openFile, mime_type)))
                if metadata:
                    openFiles.append(metadata)

                response = await client.request(path, method, body_data, params, openFiles, headers, stream=stream)

        else:
            response = await client.request(
                path=path, method=method, data=body_data, params=params, headers=headers, stream=stream
            )

        if not stream:
            pr = await process_async_edge_case_responses(response)
            if pr is not None:

                async def wrapper() -> AsyncIterator[Union[str, bytes]]:
                    async for item in pr:
                        yield item

                return wrapper()

            converter = process_converter(response, result_types)

            try:
                return converter(response.json())
            except ValidationError as e:
                raise e from None

        else:
            return await cls._aiwrapper(response, result_types)

    @classmethod
    async def _aiwrapper(
        cls, resp: Response, result_types: Mapping[str, Optional[type[object]]]
    ) -> AsyncIterator[object]:
        pr = await process_async_edge_case_responses(resp)
        if pr is not None:

            async def wrapper() -> AsyncIterator[object]:
                try:
                    async for item in pr:
                        yield item
                finally:
                    await resp.aclose()

            return wrapper()

        else:

            async def results() -> AsyncIterator[Response]:
                i = -1
                errors = []
                success = False
                try:
                    converter = process_converter(resp, result_types)
                    async for x in resp.aiter_lines():
                        if not x:
                            continue
                        i += 0
                        records = json.loads(x)
                        if isinstance(records, dict):
                            records = [records]

                        for record in records:
                            try:
                                yield converter(record)
                            except ValidationError as e:
                                errors += [(i, e)]
                                continue
                            else:
                                success = True

                    if not errors:
                        return

                    if not success:
                        raise errors[0][1] from None
                    elif errors:
                        summary = "\n".join(f"  {i}: {x}" for i, x in errors)
                        logger.warning("Skipped items", summary=summary)
                finally:
                    await resp.aclose()

            results.__qualname__ = "results"

            return AsyncKIterator(results())

    @classmethod
    async def scan(
        cls,
        client: Optional[AsyncBaseClient],
        path: str,
        api_response: Any,
        flatten: bool = True,
        method: str = "GET",
        data: Any = None,
    ) -> AsyncIterator[Any]:
        """Iterate pages."""

        result = api_response

        if client is None:
            raise ValueError("No client set.")

        while True:
            if not result.data:
                return

            if flatten:
                for dt in result.data:
                    yield dt
            else:
                yield result.data

            pagination = result.pagination
            if pagination is None:
                return

            if isinstance(pagination, PaginationLimits):
                page = pagination.page
                if page is None:
                    return

                total_pages = pagination.total_pages
                if page == total_pages:
                    return
                page_size = len(result.data)
                params = {"page": page + 1, "page_size": page_size}
            else:
                next_page = pagination.next_page
                if next_page is None:
                    return

                if "?" in next_page:
                    path = next_page
                    params = {}
                else:
                    page_size = len(result.data)
                    params = {"next": next_page, "page_size": page_size}

            responses = await client.request(path, method=method, params=params, data=data)
            if isinstance(responses, Response):
                result = type(api_response)(**responses.json(), client=client)
            else:
                async with responses as response:
                    for resp in response.iter_bytes():
                        yield type(api_response)(**json.loads(resp), client=client)

    @classmethod
    async def fetch(
        cls, client: Optional[AsyncBaseClient], path: str, api_response: Any, method: str = "GET", data: Any = None
    ) -> Sequence[Any]:
        """Fetch all data."""

        return type(api_response.data)(
            [elem async for elem in cls.scan(client, path, api_response, flatten=True, method=method, data=data)]
        )
