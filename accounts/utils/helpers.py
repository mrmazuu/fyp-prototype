import logging
import sys

role_messages = {
    "ADMIN": "You can manage all system activities as an Admin.",
    "User": "You can track and submit your activities as a User.",
    "Viewer": "You have read-only access as a Viewer.",
}


def create_welcome_msg(name=None, role=None):
    if (role := role.upper()) in role_messages.keys() and isinstance(name, str):
        first_name = name.split()[0]
        return f"Welcome {first_name}, {role_messages[role]}"
    return "Welcome!"


def normalize_userinfo(data):
    user_role = data["role"]
    user_email = data["email"]
    full_name = data["name"]
    created_at = data.get("created_at")

    user_info = {
        "name": full_name.title(),
        "email": user_email,
        "role": user_role.title(),
    }
    if created_at:
        user_info["date"] = created_at
    return user_info


def create_logger(
    log_level: str = "INFO", module_name: str = "__main__"
) -> logging.Logger:
    """
    Creates and configures a logger with separate stdout and stderr handlers.

    :param log_level: Logging level as string (e.g., 'DEBUG', 'INFO', 'ERROR').
    :param module_name: Usually __name__ from the calling module.
    :return: Configured logger instance.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Stdout: DEBUG, INFO, WARNING
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)
    stdout_handler.setFormatter(formatter)

    # Stderr: ERROR, CRITICAL
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    return logger
