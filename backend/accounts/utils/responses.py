from rest_framework import status
from rest_framework.response import Response


def error_response(message, code=status.HTTP_400_BAD_REQUEST, errors=None):
    """Utility function for consistent error responses."""
    response_data = {"success": False, "message": message}
    if errors is not None:
        response_data["errors"] = errors
    return Response(response_data, status=code)


def success_response(message, code=status.HTTP_200_OK, **kwargs):
    """Utility function for consistent success responses."""
    response_data = {"success": True, "message": message}
    if kwargs:
        response_data.update(kwargs)

    return Response(response_data, status=code)
