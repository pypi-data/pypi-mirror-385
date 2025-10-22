"""
Response History.

This module provides a deque-based class for storing T objects
from API calls, allowing users to inspect request/response history.
"""

from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Iterator
from typing import Generic, Optional, TypeVar

import httpx

T = TypeVar("T")


class History(Generic[T]):
    """
    A deque-based class for storing and managing T objects.

    This class provides a fixed-size deque that stores HTTP responses from API calls,
    allowing users to inspect the history of requests and responses.

    Attributes:
        maxlen (int): Maximum number of responses to store. Defaults to 100.
        _history (deque): Internal deque storing T objects.

    Examples:
        >>> history = ResponseHistory(maxlen=50)
        >>> history.append(response)
        >>> latest = history.latest()
        >>> all_responses = list(history)
    """

    def __init__(self, maxlen: int = 100) -> None:
        """
        Initialize the ResponseHistory.

        Args:
            maxlen: Maximum number of responses to store. When the deque is full,
                   adding a new response will remove the oldest one. Defaults to 100.
        """
        self.maxlen: int = maxlen
        self._history: deque[T] = deque(maxlen=maxlen)
        self._lock: asyncio.Lock = asyncio.Lock()

    def append(self, response: T) -> None:
        self._history.append(response)

    async def async_append(self, response: T) -> None:
        async with self._lock:
            self._history.append(response)

    def clear(self) -> None:
        """Clear all responses from the history."""
        self._history.clear()

    def latest(self) -> Optional[T]:
        """
        Get the most recent response from the history.

        Returns:
            The most recent T object, or None if history is empty.
        """
        try:
            return self._history[-1]
        except IndexError:
            return None

    def oldest(self) -> Optional[T]:
        """
        Get the oldest response from the history.

        Returns:
            The oldest T object, or None if history is empty.
        """
        try:
            return self._history[0]
        except IndexError:
            return None

    def __len__(self) -> int:
        """
        Get the number of responses in the history.

        Returns:
            The number of stored responses.
        """
        return len(self._history)

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over the responses in the history.

        Yields:
            T objects in the order they were added (oldest to newest).
        """
        return iter(self._history)

    def __getitem__(self, index: int) -> T:
        """
        Get a response by index.

        Args:
            index: The index of the response to retrieve. Negative indices
                  are supported (e.g., -1 for the latest response).

        Returns:
            The T object at the specified index.

        Raises:
            IndexError: If the index is out of range.
        """
        return self._history[index]


class ResponseHistory(History[httpx.Response]):
    """
    A history of HTTP responses.

    This class provides methods to retrieve information about the responses
    stored in the history, such as status codes, successful responses, and error
    responses.
    """

    def get_status_codes(self) -> list[int]:
        """
        Get a list of all status codes from stored responses.

        Returns:
            A list of HTTP status codes from all stored responses.
        """
        return [response.status_code for response in self._history]

    def get_successful_responses(self) -> list[httpx.Response]:
        """
        Get all successful responses (status codes 2xx).

        Returns:
            A list of T objects with successful status codes.
        """
        return [response for response in self._history if response.is_success]

    def get_error_responses(self) -> list[httpx.Response]:
        """
        Get all error responses (status codes 4xx and 5xx).

        Returns:
            A list of T objects with error status codes.
        """
        return [response for response in self._history if response.is_error]

    def filter_by_status_code(self, status_code: int) -> list[httpx.Response]:
        """
        Filter responses by a specific status code.

        Args:
            status_code: The HTTP status code to filter by.

        Returns:
            A list of T objects matching the status code.
        """
        return [response for response in self._history if response.status_code == status_code]

    def filter_by_url_pattern(self, pattern: str) -> list[httpx.Response]:
        """
        Filter responses by URL pattern.

        Args:
            pattern: A string pattern to match in the request URL.

        Returns:
            A list of T objects whose request URLs contain the pattern.
        """
        return [response for response in self._history if pattern in str(response.url)]


class RequestHistory(History[httpx.Request]):
    """
    A history of HTTP requests.

    This class provides methods to retrieve information about the requests
    stored in the history, such as status codes, successful responses, and error
    responses.
    """
