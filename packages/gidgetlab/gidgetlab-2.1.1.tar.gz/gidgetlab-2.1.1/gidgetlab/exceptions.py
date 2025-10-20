"""Gidgetlab's exceptions"""

import http
from typing import Any, Optional


class GitLabException(Exception):
    """Base exception for this library."""


class ValidationFailure(GitLabException):
    """An exception representing failed validation of a webhook event."""

    # https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#secret-token


class HTTPException(GitLabException):
    """A general exception to represent HTTP responses."""

    def __init__(self, status_code: http.HTTPStatus, *args: Any) -> None:
        self.status_code = status_code
        if args:
            super().__init__(*args)
        else:
            super().__init__(status_code.phrase)


class RedirectionException(HTTPException):
    """Exception for 3XX HTTP responses."""


class BadRequest(HTTPException):
    """The request is invalid.

    Used for 4XX HTTP errors.
    """

    # https://docs.gitlab.com/ce/api/#data-validation-and-error-reporting


class RateLimitExceeded(BadRequest):
    """Request rejected due to the rate limit being exceeded."""

    # Technically rate_limit is of type gidgetlab.sansio.RateLimit, but a
    # circular import comes about if you try to properly declare it.
    def __init__(self, rate_limit: Any, *args: Any) -> None:
        self.rate_limit = rate_limit

        if not args:
            super().__init__(http.HTTPStatus.FORBIDDEN, "rate limit exceeded")
        else:
            super().__init__(http.HTTPStatus.FORBIDDEN, *args)


class InvalidField(BadRequest):
    """A field in the request is invalid.

    Represented by a 422 HTTP Response. Details of what fields were
    invalid are stored in the errors attribute.
    """

    def __init__(self, errors: Any, *args: Any) -> None:
        """Store the error details."""
        self.errors = errors
        super().__init__(http.HTTPStatus.UNPROCESSABLE_ENTITY, *args)


class GitLabBroken(HTTPException):
    """Exception for 5XX HTTP responses."""


class GraphQLException(GitLabException):
    """Base exception for the GraphQL v4 API."""

    def __init__(self, message: str, response: Any) -> None:
        self.response = response
        super().__init__(message)


class BadGraphQLRequest(GraphQLException):
    """A 4XX HTTP response."""

    def __init__(self, status_code: http.HTTPStatus, response: Any) -> None:
        assert 399 < status_code < 500
        self.status_code = status_code
        try:
            message = response["errors"][0]["message"]
        except (TypeError, KeyError):
            message = response
        super().__init__(message, response)


class GraphQLAuthorizationFailure(BadGraphQLRequest):
    """401 HTTP response to a bad oauth token."""

    def __init__(self, response: Any) -> None:
        super().__init__(http.HTTPStatus(401), response)


class QueryError(GraphQLException):
    """An error occurred while attempting to handle a GraphQL v4 query."""

    def __init__(self, response: Any) -> None:
        super().__init__(response["errors"][0]["message"], response)


class GraphQLResponseTypeError(GraphQLException):
    """The GraphQL response has an unexpected content type."""

    def __init__(self, content_type: Optional[str], response: Any) -> None:
        super().__init__(
            f"Response had an unexpected content-type: '{content_type!r}'", response
        )
