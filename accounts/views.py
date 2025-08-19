from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth import login, logout
from django.db import DatabaseError
from drf_spectacular.utils import extend_schema
from accounts.serializers import UserSerializer, LoginSerializer, UserInfoSerializer
from accounts.utils import (
    create_welcome_msg,
    normalize_userinfo,
    create_logger,
    success_response,
    error_response,
)

logger = create_logger(__name__)


@extend_schema(
    summary="User Signup",
    description="Register a new user with `email`, `name`, `password`, and `role`. "
    "Both email and name will be stored in lowercase.",
    request=UserSerializer,
    responses={
        201: {
            "example": {
                "success": True,
                "message": "User registered successfully",
                "user_info": {
                    "name": "Ali Hamza",
                    "email": "user@example.com",
                    "role": "ADMIN",
                },
            }
        },
        400: {"example": {"success": False, "message": "Invalid data"}},
        500: {
            "example": {
                "success": False,
                "message": "Database error occurred while creating user",
            }
        },
    },
    tags=["Authentication"],
)
@api_view(["POST"])
def signup_view(request):
    """
    User Signup API
    """
    
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            logger.info(
                "User created successfully",
                extra={"user_id": user.user_id, "email": user.email, "role": user.role},
            )
            return success_response(
                message="User registered successfully",
                code=status.HTTP_201_CREATED,
                user_info=normalize_userinfo(serializer.data),
            )
        except DatabaseError as db_err:
            logger.error("Database error during signup", exc_info=True)
            return error_response(
                message="Database error occurred while creating user",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error("Unexpected error during signup", exc_info=True)
            return error_response(
                message=f"Unexpected error: {str(e)}",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    logger.warning("Invalid signup data", extra={"errors": serializer.errors})
    return error_response(message="Invalid data", errors=serializer.errors)


@extend_schema(
    summary="User Login",
    description="Authenticate a user by `email`, `password`, and `role`. "
    "Returns a welcome message depending on role.",
    request=LoginSerializer,
    responses={
        200: {
            "example": {
                "success": True,
                "message": "Welcome!",
                "user_info": {
                    "name": "Ali Hamza",
                    "email": "user@example.com",
                    "role": "ADMIN",
                },
            }
        },
        400: {"example": {"success": False, "message": "Invalid credentials"}},
        500: {"example": {"success": False, "message": "Error starting session"}},
    },
    tags=["Authentication"],
)
@api_view(["POST"])
def login_view(request):
    """
    User Login API with role validation
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Invalid login credentials", extra={"errors": serializer.errors})
        return error_response(message="Invalid credentials", errors=serializer.errors)

    user = serializer.validated_data["user"]
    try:
        login(request, user)
        logger.info(
            "User logged in successfully",
            extra={"user_id": user.user_id, "email": user.email, "role": user.role},
        )
    except Exception as e:
        logger.error("Error starting session during login", exc_info=True)
        return error_response(
            message=f"Error starting session: {str(e)}",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    welcome_msg = create_welcome_msg(user.name, user.role)
    return success_response(message=welcome_msg)


@extend_schema(
    summary="Get User Info",
    description="Retrieve the currently logged-in user's profile information.",
    responses={
        200: UserInfoSerializer,
        401: {"example": {"success": False, "message": "Invalid user session"}},
    },
    tags=["User"],
)
@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    """
    Get logged-in user's information
    """
    logger.info("User info request received", extra={"user_id": getattr(request.user, "user_id", None)})
    try:
        serializer = UserInfoSerializer(request.user)
        userinfo = normalize_userinfo(serializer.data)
        welcome_message = create_welcome_msg(userinfo["name"], userinfo["role"])
        logger.info(
            "User info retrieved successfully",
            extra={"user_id": request.user.user_id, "email": request.user.email},
        )
        return success_response(message=welcome_message, user_info=userinfo)
    except NotAuthenticated:
        logger.warning("Unauthenticated access to user info")
        return error_response(
            message="Invalid or missing authentication credentials",
            code=status.HTTP_401_UNAUTHORIZED,
        )
    except AttributeError:
        logger.error("Invalid session: request.user missing attributes")
        return error_response(
            message="Invalid user session", code=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        logger.error("Unexpected error while fetching user info", exc_info=True)
        return error_response(
            message=f"Unexpected error: {str(e)}",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )