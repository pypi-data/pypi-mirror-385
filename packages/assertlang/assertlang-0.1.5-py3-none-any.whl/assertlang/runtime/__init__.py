"""AssertLang runtime support modules."""

from assertlang.runtime.contracts import (
    ContractViolationError,
    OldValue,
    ValidationMode,
    capture_old_values,
    check_invariant,
    check_postcondition,
    check_precondition,
    get_validation_mode,
    set_validation_mode,
    should_check_invariants,
    should_check_postconditions,
    should_check_preconditions,
)

from assertlang.runtime.stdlib import (
    Result,
    Ok,
    Error,
    al_str,
    al_list,
    al_math,
    al_result,
)

__all__ = [
    # Contract validation
    "ContractViolationError",
    "OldValue",
    "ValidationMode",
    "capture_old_values",
    "check_invariant",
    "check_postcondition",
    "check_precondition",
    "get_validation_mode",
    "set_validation_mode",
    "should_check_invariants",
    "should_check_postconditions",
    "should_check_preconditions",

    # Standard library
    "Result",
    "Ok",
    "Error",
    "al_str",
    "al_list",
    "al_math",
    "al_result",
]
