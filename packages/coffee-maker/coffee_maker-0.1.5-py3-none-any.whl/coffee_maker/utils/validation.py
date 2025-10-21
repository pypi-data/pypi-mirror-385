"""Common validation utilities for type checking and value validation.

This module provides reusable validation functions to reduce code duplication
and ensure consistent error messages across the codebase.

Example:
    >>> from coffee_maker.utils.validation import require_type, require_one_of
    >>>
    >>> # Type validation
    >>> config = require_type(value, dict, "config")
    >>>
    >>> # Value validation
    >>> tier = require_one_of(tier_str, ["tier1", "tier2", "tier3"], "tier")
"""

from typing import Any, Iterable, Optional, Type, TypeVar, Union

T = TypeVar("T")


def require_type(
    value: Any,
    expected_type: Union[Type[T], tuple],
    param_name: str = "value",
) -> T:
    """Require value to be of expected type.

    Args:
        value: Value to validate
        expected_type: Expected type or tuple of types
        param_name: Name of parameter for error message

    Returns:
        The validated value (for chaining)

    Raises:
        TypeError: If value is not of expected type

    Example:
        >>> config = require_type(user_input, dict, "config")
        >>> rate_tracker = require_type(tracker, RateLimitTracker, "rate_tracker")
    """
    if not isinstance(value, expected_type):
        if isinstance(expected_type, tuple):
            type_names = " or ".join(t.__name__ for t in expected_type)
        else:
            type_names = expected_type.__name__

        raise TypeError(f"{param_name} must be {type_names}, got {type(value).__name__}")
    return value


def require_one_of(
    value: Any,
    options: Iterable[Any],
    param_name: str = "value",
) -> Any:
    """Require value to be one of the given options.

    Args:
        value: Value to validate
        options: Iterable of valid options
        param_name: Name of parameter for error message

    Returns:
        The validated value (for chaining)

    Raises:
        ValueError: If value not in options

    Example:
        >>> tier = require_one_of(tier_str, ["tier1", "tier2", "tier3"], "tier")
        >>> provider = require_one_of(prov, ["openai", "gemini"], "provider")
    """
    options_list = list(options)
    if value not in options_list:
        raise ValueError(f"{param_name} must be one of {options_list}, got {value!r}")
    return value


def require_non_empty(
    value: Union[str, list, dict, set, tuple],
    param_name: str = "value",
) -> Any:
    """Require value to be non-empty.

    Works with strings, lists, dicts, sets, tuples.

    Args:
        value: Value to validate
        param_name: Name of parameter for error message

    Returns:
        The validated value (for chaining)

    Raises:
        ValueError: If value is empty

    Example:
        >>> name = require_non_empty(model_name, "model_name")
        >>> items = require_non_empty(config_list, "fallback_configs")
    """
    if not value:
        raise ValueError(f"{param_name} cannot be empty")
    return value


def require_positive(
    value: Union[int, float],
    param_name: str = "value",
    allow_zero: bool = False,
) -> Union[int, float]:
    """Require value to be positive (optionally allowing zero).

    Args:
        value: Numeric value to validate
        param_name: Name of parameter for error message
        allow_zero: Whether to allow zero (default: False)

    Returns:
        The validated value (for chaining)

    Raises:
        ValueError: If value is not positive

    Example:
        >>> tokens = require_positive(token_count, "tokens", allow_zero=True)
        >>> cost = require_positive(total_cost, "cost")
    """
    0 if allow_zero else 0
    operator = ">=" if allow_zero else ">"

    if allow_zero:
        if value < 0:
            raise ValueError(f"{param_name} must be {operator} 0, got {value}")
    else:
        if value <= 0:
            raise ValueError(f"{param_name} must be {operator} 0, got {value}")

    return value


def require_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    param_name: str = "value",
) -> Union[int, float]:
    """Require value to be within a range.

    Args:
        value: Numeric value to validate
        min_value: Minimum allowed value (inclusive, optional)
        max_value: Maximum allowed value (inclusive, optional)
        param_name: Name of parameter for error message

    Returns:
        The validated value (for chaining)

    Raises:
        ValueError: If value is out of range

    Example:
        >>> safety_margin = require_range(margin, 1, 10, "safety_margin")
        >>> temperature = require_range(temp, 0.0, 2.0, "temperature")
    """
    if min_value is not None and value < min_value:
        raise ValueError(f"{param_name} must be >= {min_value}, got {value}")

    if max_value is not None and value > max_value:
        raise ValueError(f"{param_name} must be <= {max_value}, got {value}")

    return value


def require_not_none(
    value: Optional[T],
    param_name: str = "value",
) -> T:
    """Require value to not be None.

    Args:
        value: Value to validate
        param_name: Name of parameter for error message

    Returns:
        The validated value (for chaining)

    Raises:
        ValueError: If value is None

    Example:
        >>> config = require_not_none(config_dict, "config")
        >>> model = require_not_none(primary_model, "primary_model")
    """
    if value is None:
        raise ValueError(f"{param_name} cannot be None")
    return value


def validate_url(
    url: str,
    param_name: str = "url",
    require_https: bool = False,
) -> str:
    """Validate that a string is a valid URL.

    Args:
        url: URL string to validate
        param_name: Name of parameter for error message
        require_https: Whether to require HTTPS (default: False)

    Returns:
        The validated URL (for chaining)

    Raises:
        ValueError: If URL is invalid

    Example:
        >>> api_url = validate_url(user_url, "api_url", require_https=True)
    """
    require_non_empty(url, param_name)

    if require_https and not url.startswith("https://"):
        raise ValueError(f"{param_name} must start with https://, got {url!r}")

    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError(f"{param_name} must be a valid URL (http:// or https://), got {url!r}")

    return url
