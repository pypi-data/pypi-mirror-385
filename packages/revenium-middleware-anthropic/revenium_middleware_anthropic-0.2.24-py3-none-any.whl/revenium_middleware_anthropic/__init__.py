"""
Revenium Middleware for Anthropic Python SDK

This library automatically hooks anthropic.resources.messages.create using wrapt,
and logs token usage after each request. You can customize or extend this logging
logic later to add user or organization metadata for metering purposes.

Now supports AWS Bedrock integration for routing Anthropic Claude models
through Amazon Bedrock while maintaining the same metering functionality.

Auto-initialization: The middleware is automatically initialized on import for
a simple "just works" experience. For explicit control, use the exported
initialize() function.
"""

import logging
import os

# Import the middleware module to ensure the wrapt decorators are executed
from . import middleware
from .middleware import create_wrapper, usage_context

# Import core components
from .provider import Provider, detect_provider, get_provider_metadata, is_bedrock_provider

# Set up logger for initialization
logger = logging.getLogger("revenium_middleware_anthropic.init")


def initialize():
    """
    Explicitly initialize the Revenium middleware.

    This function can be called manually for explicit control over initialization,
    or it's called automatically on import with graceful fallback.

    Returns:
        bool: True if initialization succeeded, False otherwise
    """
    try:
        # Check if required environment variables are set
        api_key = os.getenv("REVENIUM_METERING_API_KEY")
        if not api_key:
            logger.debug("REVENIUM_METERING_API_KEY not set - middleware will not meter requests")
            return False

        # The middleware is automatically activated by importing create_wrapper
        # which uses @wrapt.patch_function_wrapper decorator
        logger.debug("Revenium middleware initialized successfully")
        return True

    except Exception as e:
        logger.debug(f"Failed to initialize Revenium middleware: {e}")
        return False


def is_initialized():
    """
    Check if the middleware has been initialized.

    Returns:
        bool: True if middleware is active and ready to meter requests
    """
    try:
        # Check if environment is properly configured
        api_key = os.getenv("REVENIUM_METERING_API_KEY")
        base_url = os.getenv("REVENIUM_METERING_BASE_URL")

        return bool(api_key and base_url)
    except Exception:
        return False


# Auto-initialize with graceful fallback
try:
    _auto_init_success = initialize()
    if _auto_init_success:
        logger.debug("Auto-initialization successful")
    else:
        logger.debug("Auto-initialization skipped - manual configuration may be needed")
except Exception as e:
    # Log debug message but don't throw
    # Allow manual configuration later
    logger.debug(f"Auto-initialization failed: {e}")
    _auto_init_success = False

# Export functions for explicit control
__all__ = [
    # Core middleware components
    "create_wrapper",
    "usage_context",

    # Provider detection
    "Provider",
    "detect_provider",
    "get_provider_metadata",
    "is_bedrock_provider",

    # Initialization control
    "initialize",
    "is_initialized",
]
