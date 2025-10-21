# -*- coding: utf-8 -*-
"""Header processing utilities for dynamic environment injection in translate module.

Location: ./mcpgateway/translate_header_utils.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Manav Gupta

Header processing utilities for dynamic environment variable injection in mcpgateway.translate.
"""

# Standard
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

# Security constants
ALLOWED_HEADERS_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9\-]*$")
MAX_HEADER_VALUE_LENGTH = 4096
MAX_ENV_VAR_NAME_LENGTH = 64


class HeaderMappingError(Exception):
    """Raised when header mapping configuration is invalid."""


def validate_header_mapping(header_name: str, env_var_name: str) -> None:
    """Validate header name and environment variable name.

    Args:
        header_name: HTTP header name
        env_var_name: Environment variable name

    Raises:
        HeaderMappingError: If validation fails
    """
    if not ALLOWED_HEADERS_REGEX.match(header_name):
        raise HeaderMappingError(f"Invalid header name '{header_name}' - must contain only alphanumeric characters and hyphens")

    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", env_var_name):
        raise HeaderMappingError(f"Invalid environment variable name '{env_var_name}' - must start with letter/underscore and contain only alphanumeric characters and underscores")

    if len(env_var_name) > MAX_ENV_VAR_NAME_LENGTH:
        raise HeaderMappingError(f"Environment variable name too long: {env_var_name}")


def sanitize_header_value(value: str, max_length: int = MAX_HEADER_VALUE_LENGTH) -> str:
    """Sanitize header value for environment variable injection.

    Args:
        value: Raw header value
        max_length: Maximum allowed length for the value

    Returns:
        Sanitized value safe for environment variable
    """
    if len(value) > max_length:
        logger.warning(f"Header value truncated from {len(value)} to {max_length} characters")
        value = value[:max_length]

    # Remove potentially dangerous characters
    value = re.sub(r"[^\x20-\x7E]", "", value)  # Only printable ASCII
    value = value.replace("\x00", "")  # Remove null bytes

    return value


def parse_header_mappings(header_mappings: List[str]) -> Dict[str, str]:
    """Parse header-to-environment mappings from CLI arguments.

    Args:
        header_mappings: List of "HEADER=ENV_VAR" strings

    Returns:
        Dictionary mapping header names to environment variable names

    Raises:
        HeaderMappingError: If any mapping is invalid
    """
    mappings = {}

    for mapping in header_mappings:
        if "=" not in mapping:
            raise HeaderMappingError(f"Invalid mapping format '{mapping}' - expected HEADER=ENV_VAR")

        header_name, env_var_name = mapping.split("=", 1)
        header_name = header_name.strip()
        env_var_name = env_var_name.strip()

        if not header_name or not env_var_name:
            raise HeaderMappingError(f"Empty header name or environment variable name in '{mapping}'")

        validate_header_mapping(header_name, env_var_name)

        if header_name in mappings:
            raise HeaderMappingError(f"Duplicate header mapping for '{header_name}'")

        mappings[header_name] = env_var_name

    return mappings


def extract_env_vars_from_headers(request_headers: Dict[str, str], header_mappings: Dict[str, str]) -> Dict[str, str]:
    """Extract environment variables from request headers.

    Args:
        request_headers: HTTP request headers
        header_mappings: Mapping of header names to environment variable names

    Returns:
        Dictionary of environment variable name -> sanitized value
    """
    env_vars = {}

    for header_name, env_var_name in header_mappings.items():
        # Case-insensitive header matching
        header_value = None
        for req_header, value in request_headers.items():
            if req_header.lower() == header_name.lower():
                header_value = value
                break

        if header_value is not None:
            try:
                sanitized_value = sanitize_header_value(header_value)
                if sanitized_value:  # Only add non-empty values
                    env_vars[env_var_name] = sanitized_value
                    logger.debug(f"Mapped header {header_name} to {env_var_name}")
                else:
                    logger.warning(f"Header {header_name} value became empty after sanitization")
            except Exception as e:
                logger.warning(f"Failed to process header {header_name}: {e}")

    return env_vars
