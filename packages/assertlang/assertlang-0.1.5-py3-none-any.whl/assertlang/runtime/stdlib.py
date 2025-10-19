"""
AssertLang Standard Library Runtime

This module provides runtime support for AssertLang standard library functions
when transpiling to Python. It includes:

- Result type (Ok/Error pattern)
- String module functions
- List module functions
- Math module functions
- Result module functions

The modules are designed to NOT override Python built-ins by making them callable.
"""

from __future__ import annotations
from typing import Any, TypeVar, Generic, Union
import math as _py_math

# ============================================================================
# Result Type
# ============================================================================

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    """Result type for Ok/Error pattern."""
    def __init__(self, success: bool, value: Any = None, error: Any = None):
        self.success = success
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.success

    def is_error(self) -> bool:
        return not self.success

    def __repr__(self):
        if self.success:
            return f"Ok({self.value!r})"
        else:
            return f"Error({self.error!r})"


def Ok(value: T) -> Result[T, Any]:
    """Create a successful Result."""
    return Result(success=True, value=value)


def Error(error: E) -> Result[Any, E]:
    """Create an error Result."""
    return Result(success=False, error=error)


# ============================================================================
# String Module
# ============================================================================

class StrModule:
    """
    AssertLang string module.

    Provides string operations while preserving Python's built-in str() function.
    """

    def __call__(self, *args, **kwargs):
        """Preserve Python's built-in str() conversion."""
        return str(*args, **kwargs)

    @staticmethod
    def length(s: str) -> int:
        """Return the length of a string."""
        return len(s)

    @staticmethod
    def contains(haystack: str, needle: str) -> bool:
        """Check if a string contains a substring."""
        return needle in haystack

    @staticmethod
    def upper(s: str) -> str:
        """Convert string to uppercase."""
        return s.upper()

    @staticmethod
    def lower(s: str) -> str:
        """Convert string to lowercase."""
        return s.lower()

    @staticmethod
    def trim(s: str) -> str:
        """Remove leading/trailing whitespace."""
        return s.strip()

    @staticmethod
    def split(s: str, delimiter: str = " ") -> list[str]:
        """Split string by delimiter."""
        return s.split(delimiter)

    @staticmethod
    def join(strings: list[str], separator: str = "") -> str:
        """Join strings with separator."""
        return separator.join(strings)

    @staticmethod
    def replace(s: str, old: str, new: str) -> str:
        """Replace all occurrences of old with new."""
        return s.replace(old, new)

    @staticmethod
    def substring(s: str, start: int, end: int = None) -> str:
        """Extract substring from start to end."""
        if end is None:
            return s[start:]
        return s[start:end]

    @staticmethod
    def starts_with(s: str, prefix: str) -> bool:
        """Check if string starts with prefix."""
        return s.startswith(prefix)

    @staticmethod
    def ends_with(s: str, suffix: str) -> bool:
        """Check if string ends with suffix."""
        return s.endswith(suffix)


# Create module instance (callable to preserve str() behavior)
al_str = StrModule()


# ============================================================================
# List Module
# ============================================================================

class ListModule:
    """
    AssertLang list module.

    Provides list operations while preserving Python's built-in list() function.
    """

    def __call__(self, *args, **kwargs):
        """Preserve Python's built-in list() conversion."""
        return list(*args, **kwargs)

    @staticmethod
    def length(lst: list) -> int:
        """Return the length of a list."""
        return len(lst)

    @staticmethod
    def get(lst: list, index: int) -> Any:
        """Get element at index."""
        return lst[index]

    @staticmethod
    def append(lst: list, item: Any) -> list:
        """Append item to list (returns new list)."""
        result = lst.copy()
        result.append(item)
        return result

    @staticmethod
    def prepend(lst: list, item: Any) -> list:
        """Prepend item to list (returns new list)."""
        return [item] + lst

    @staticmethod
    def concat(lst1: list, lst2: list) -> list:
        """Concatenate two lists."""
        return lst1 + lst2

    @staticmethod
    def slice(lst: list, start: int, end: int = None) -> list:
        """Extract slice from start to end."""
        if end is None:
            return lst[start:]
        return lst[start:end]

    @staticmethod
    def first(lst: list) -> Any:
        """Get first element."""
        return lst[0] if lst else None

    @staticmethod
    def last(lst: list) -> Any:
        """Get last element."""
        return lst[-1] if lst else None

    @staticmethod
    def is_empty(lst: list) -> bool:
        """Check if list is empty."""
        return len(lst) == 0

    @staticmethod
    def contains(lst: list, item: Any) -> bool:
        """Check if list contains item."""
        return item in lst

    @staticmethod
    def index_of(lst: list, item: Any) -> int:
        """Find index of item (-1 if not found)."""
        try:
            return lst.index(item)
        except ValueError:
            return -1

    @staticmethod
    def reverse(lst: list) -> list:
        """Reverse list (returns new list)."""
        return list(reversed(lst))

    @staticmethod
    def sort(lst: list) -> list:
        """Sort list (returns new list)."""
        return sorted(lst)


# Create module instance (callable to preserve list() behavior)
al_list = ListModule()


# ============================================================================
# Math Module
# ============================================================================

class MathModule:
    """
    AssertLang math module.

    Provides math operations.
    """

    @staticmethod
    def abs(x: float) -> float:
        """Absolute value."""
        return abs(x)

    @staticmethod
    def ceil(x: float) -> int:
        """Ceiling (round up)."""
        return _py_math.ceil(x)

    @staticmethod
    def floor(x: float) -> int:
        """Floor (round down)."""
        return _py_math.floor(x)

    @staticmethod
    def round(x: float, digits: int = 0) -> float:
        """Round to n digits."""
        return round(x, digits)

    @staticmethod
    def min(a: float, b: float) -> float:
        """Minimum of two numbers."""
        return min(a, b)

    @staticmethod
    def max(a: float, b: float) -> float:
        """Maximum of two numbers."""
        return max(a, b)

    @staticmethod
    def pow(base: float, exp: float) -> float:
        """Power operation."""
        return base ** exp

    @staticmethod
    def sqrt(x: float) -> float:
        """Square root."""
        return _py_math.sqrt(x)

    @staticmethod
    def sin(x: float) -> float:
        """Sine."""
        return _py_math.sin(x)

    @staticmethod
    def cos(x: float) -> float:
        """Cosine."""
        return _py_math.cos(x)

    @staticmethod
    def tan(x: float) -> float:
        """Tangent."""
        return _py_math.tan(x)

    @staticmethod
    def log(x: float) -> float:
        """Natural logarithm."""
        return _py_math.log(x)

    @staticmethod
    def log10(x: float) -> float:
        """Base-10 logarithm."""
        return _py_math.log10(x)

    @staticmethod
    def exp(x: float) -> float:
        """e^x."""
        return _py_math.exp(x)

    # Constants
    PI = _py_math.pi
    E = _py_math.e


# Create module instance
al_math = MathModule()


# ============================================================================
# Result Module
# ============================================================================

class ResultModule:
    """
    AssertLang result module.

    Provides operations on Result types.
    """

    @staticmethod
    def is_ok(result: Result) -> bool:
        """Check if Result is Ok."""
        return result.is_ok()

    @staticmethod
    def is_error(result: Result) -> bool:
        """Check if Result is Error."""
        return result.is_error()

    @staticmethod
    def unwrap(result: Result) -> Any:
        """Unwrap Ok value (raises if Error)."""
        if result.is_ok():
            return result.value
        raise ValueError(f"Cannot unwrap Error: {result.error}")

    @staticmethod
    def unwrap_or(result: Result, default: Any) -> Any:
        """Unwrap Ok value or return default."""
        if result.is_ok():
            return result.value
        return default

    @staticmethod
    def map(result: Result, func) -> Result:
        """Map function over Ok value."""
        if result.is_ok():
            return Ok(func(result.value))
        return result


# Create module instance
al_result = ResultModule()


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Result type
    "Result",
    "Ok",
    "Error",

    # Modules
    "al_str",
    "al_list",
    "al_math",
    "al_result",

    # For backward compatibility (but these override built-ins!)
    "StrModule",
    "ListModule",
    "MathModule",
    "ResultModule",
]
