"""
Compatibility shim — moved to kelvin.api.base.error

Deprecated: import from kelvin.api.base.error instead.
"""

import warnings

warnings.warn(
    "kelvin.api.client.error is deprecated — use kelvin.api.base.error instead",
    DeprecationWarning,
    stacklevel=2,
)

from kelvin.api.base.error import APIError, AuthenticationError, ClientError, LoginError, LogoutError, ResponseError

__all__ = ["ClientError", "AuthenticationError", "LoginError", "LogoutError", "APIError", "ResponseError"]
