from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
    ParseError,
    MethodNotAllowed,
    NotFound,
    UnsupportedMediaType,
    Throttled,
)
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from .responses import error_response


# assuming you already have error_response(message, code, errors=None)
def custom_exception_handler(exc, context):
    """
    Custom global exception handler to ensure consistent error responses.
    Handles all known DRF and Django exceptions gracefully.
    """

    # Authentication errors
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return error_response(
            message="Invalid or missing authentication credentials",
            code=status.HTTP_401_UNAUTHORIZED,
        )

    # Permission errors
    if isinstance(exc, (PermissionDenied, DjangoPermissionDenied)):
        return error_response(
            message="You do not have permission to perform this action",
            code=status.HTTP_403_FORBIDDEN,
            errors=exc.detail
        )

    # Validation errors
    if isinstance(exc, ValidationError):
        return error_response(
            message="Invalid input data",
            code=status.HTTP_400_BAD_REQUEST,
            errors=exc.detail,  # keep field-level details
        )

    # Parsing errors (malformed JSON, etc.)
    if isinstance(exc, ParseError):
        return error_response(
            message="Malformed request data",
            code=status.HTTP_400_BAD_REQUEST,
        )

    # Method not allowed
    if isinstance(exc, MethodNotAllowed):
        return error_response(
            message=f"Method '{exc.method}' not allowed on this endpoint",
            code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # Not found (API or resource missing)
    if isinstance(exc, (NotFound, Http404)):
        return error_response(
            message="The requested resource was not found",
            code=status.HTTP_404_NOT_FOUND,
        )

    # Unsupported media type
    if isinstance(exc, UnsupportedMediaType):
        return error_response(
            message="Unsupported media type",
            code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    # Throttling (rate limits exceeded)
    if isinstance(exc, Throttled):
        return error_response(
            message="Request was throttled. Please try again later.",
            code=status.HTTP_429_TOO_MANY_REQUESTS,
            errors={"retry_after": exc.wait},
        )

    # Let DRF handle anything else it knows
    response = exception_handler(exc, context)

    # If DRF has a response (like for APIException subclasses not listed above)
    if response is not None:
        return error_response(
            message=response.data.get("detail", "An error occurred"),
            code=response.status_code,
        )

    # Unhandled/unexpected exception
    return error_response(
        message="An unexpected error occurred. Please contact support.",
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors={"error": str(exc)},
    )
