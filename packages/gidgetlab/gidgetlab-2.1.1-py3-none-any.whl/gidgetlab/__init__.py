"""An async GitLab API library"""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0+unknown"


# flake8: noqa: F401
from .exceptions import (
    GitLabException,
    ValidationFailure,
    HTTPException,
    RedirectionException,
    BadRequest,
    RateLimitExceeded,
    InvalidField,
    GitLabBroken,
    GraphQLException,
    BadGraphQLRequest,
    GraphQLAuthorizationFailure,
    QueryError,
    GraphQLResponseTypeError,
)
