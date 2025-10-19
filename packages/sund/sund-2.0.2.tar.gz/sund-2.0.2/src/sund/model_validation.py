"""
Model validation module for SUND.

This module provides functions to validate model files for common errors and issues.
"""

import logging
import re
from pathlib import Path

from .tools import _model_structure, _remove_white_space

logger = logging.getLogger(__name__)


class ModelValidationError(Exception):
    """Exception raised for model validation errors."""


def validate_model(
    model_path_or_content: str | Path,
    *,
    raise_on_error: bool = True,
    raise_on_warning: bool = False,
) -> dict[str, list[str]]:
    """
    Validate a model file or content string for common errors.

    Args:
        model_path_or_content: Path to model file or model content string
        raise_on_error: Whether to raise exceptions for validation errors
        raise_on_warning: Whether to raise exceptions for validation warnings

    Returns:
        Dictionary containing 'errors' and 'warnings' lists

    Raises:
        ModelValidationError: If validation fails and raise_on_error is True
    """
    # Load model content
    model_content = str(model_path_or_content)

    # Check if it's a file path by looking for model content markers
    # If it doesn't contain model markers, assume it's a file path
    is_model_content = "########## NAME" in model_content

    if not is_model_content:
        # Assume it's a file path
        path = Path(model_path_or_content)
        try:
            model_content = path.read_text()
        except FileNotFoundError as exc:
            error_msg = f"Model file not found: {model_path_or_content}"
            if raise_on_error:
                raise ModelValidationError(error_msg) from exc
            return {"errors": [error_msg], "warnings": []}
        except (OSError, UnicodeDecodeError) as exc:
            error_msg = f"Error reading model file '{model_path_or_content}': {exc}"
            if raise_on_error:
                raise ModelValidationError(error_msg) from exc
            return {"errors": [error_msg], "warnings": []}
        else:
            file_path = str(path.parent)
    else:
        # It's model content
        file_path = "."

    # Parse model structure
    try:
        model_structure = _model_structure(model_content, file_path)
    except Exception as exc:
        error_msg = f"Failed to parse model: {exc!s}"
        if raise_on_error:
            raise ModelValidationError(error_msg) from exc
        return {"errors": [error_msg], "warnings": []}

    # Run validation checks
    errors = []
    warnings_list = []

    # Check 1: Degradation reactions not depending on themselves
    degradation_errors = _check_degradation_reactions(model_structure)
    errors.extend(degradation_errors)

    # Check 2: Unused variables/reactions
    unused_vars = _check_unused_variables(model_structure)
    warnings_list.extend(unused_vars)

    # Check 3: Unused inputs
    unused_inputs = _check_unused_inputs(model_structure)
    warnings_list.extend(unused_inputs)

    # Check 4: Unused parameters
    unused_params = _check_unused_parameters(model_structure)
    warnings_list.extend(unused_params)

    # Check 5: Features depending on undefined variables/states/parameters
    undefined_deps = _check_undefined_dependencies(model_structure)
    errors.extend(undefined_deps)

    # Check 6: Negative signs in variables/reactions (warning)
    negative_signs = _check_negative_signs(model_structure)
    warnings_list.extend(negative_signs)

    # Check 7: Duplicate parameters/variables in derivatives
    duplicate_warnings = _check_duplicate_usage_in_derivatives(model_structure)
    warnings_list.extend(duplicate_warnings)

    # Check 8: Additional checks
    additional_errors, additional_warnings = _check_additional_issues(model_structure)
    errors.extend(additional_errors)
    warnings_list.extend(additional_warnings)

    # Handle errors and warnings
    if errors and raise_on_error:
        raise ModelValidationError(
            f"Model validation failed with {len(errors)} errors:\n"
            + "\n".join(f"- {error}" for error in errors),
        )

    if warnings_list and raise_on_warning:
        raise ModelValidationError(
            f"Model validation failed with {len(warnings_list)} warnings:\n"
            + "\n".join(f"- {warning}" for warning in warnings_list),
        )

    return {"errors": errors, "warnings": warnings_list}


def _check_degradation_reactions(model_structure: dict) -> list[str]:  # noqa: C901, PLR0912
    """Check for degradation reactions that don't depend on themselves."""
    errors = []

    # Check state equations for degradation patterns (safely handle missing keys)
    for state_name, state_info in model_structure.get("STATES", {}).items():
        # Handle different model structure formats
        if isinstance(state_info, dict) and "expression" in state_info:
            expression = state_info["expression"]
        elif isinstance(state_info, str):
            expression = state_info
        else:
            # Skip if we can't determine the expression format
            continue

        # Check if expression has negative terms (potential degradation)
        if _has_negative_terms(expression):
            # Extract variables from the expression
            referenced_vars = _extract_variables_from_expression(expression)

            # If the state itself is not referenced, it might be problematic
            # Check if this looks like a degradation (has negative terms and simple structure)
            if state_name not in referenced_vars and _looks_like_constant_degradation(expression):
                errors.append(
                    f"State '{state_name}' has degradation rate that doesn't depend on {state_name} itself: '{expression}'",  # noqa: E501
                )

    # Check variables for degradation patterns (safely handle missing keys)
    for var_name, var_info in model_structure.get("VARIABLES", {}).items():
        expression = var_info["expression"]

        # Check if variable name suggests it's a rate (contains 'rate', 'k', 'v', etc.)
        if _looks_like_rate_variable(var_name):
            potential_state = _guess_state_from_rate_name(var_name)
            if potential_state and potential_state in model_structure.get("STATES", {}):
                referenced_vars = _extract_variables_from_expression(expression)

                # Check if this variable is used in a negative context in the state derivative
                states_dict = model_structure.get("STATES", {})
                if potential_state in states_dict:
                    state_info = states_dict[potential_state]
                    # Handle different model structure formats
                    if isinstance(state_info, dict) and "expression" in state_info:
                        state_expr = state_info["expression"]
                    elif isinstance(state_info, str):
                        state_expr = state_info
                    else:
                        continue

                    is_used_negatively = _is_variable_used_negatively(var_name, state_expr)

                # If it's used negatively in the derivative but doesn't depend on the state itself
                if (is_used_negatively and potential_state not in referenced_vars) or (
                    _has_negative_terms(expression) and potential_state not in referenced_vars
                ):
                    errors.append(
                        f"Rate variable '{var_name}' = '{expression}' appears to be a degradation rate for '{potential_state}' but doesn't depend on {potential_state}",  # noqa: E501
                    )

    return errors


def _check_unused_variables(model_structure: dict) -> list[str]:  # noqa: C901, PLR0912
    """Check for unused variables/reactions."""

    # Get all defined variables (safely handle missing keys)
    defined_vars = set(model_structure.get("VARIABLES", {}).keys())

    # Get all used variables
    used_vars = set()

    # Check usage in state equations
    for state_info in model_structure.get("STATES", {}).values():
        # Handle different model structure formats
        if isinstance(state_info, dict) and "expression" in state_info:
            expression = state_info["expression"]
        elif isinstance(state_info, str):
            expression = state_info
        else:
            continue
        used_vars.update(_extract_variables_from_expression(expression))

    # Check usage in algebraic equations (for DAE models)
    alg_equations = model_structure.get("ALG_EQUATIONS", {})
    if isinstance(alg_equations, list):
        # DAE models have ALG_EQUATIONS as a list of expressions
        for alg_expr in alg_equations:
            used_vars.update(_extract_variables_from_expression(alg_expr))
    elif isinstance(alg_equations, dict):
        # Some models might have ALG_EQUATIONS as a dict
        for alg_info in alg_equations.values():
            if isinstance(alg_info, dict) and "expression" in alg_info:
                used_vars.update(_extract_variables_from_expression(alg_info["expression"]))
            elif isinstance(alg_info, str):
                used_vars.update(_extract_variables_from_expression(alg_info))

    # Check usage in other variables
    for var_info in model_structure.get("VARIABLES", {}).values():
        used_vars.update(_extract_variables_from_expression(var_info["expression"]))

    # Check usage in features
    for feature_info in model_structure.get("FEATURES", {}).values():
        used_vars.update(_extract_variables_from_expression(feature_info["expression"]))

    # Check usage in outputs
    for output_info in model_structure.get("OUTPUTS", {}).values():
        used_vars.update(_extract_variables_from_expression(output_info["expression"]))

    # Check usage in events
    for event_info in model_structure.get("EVENTS", {}).values():
        used_vars.update(_extract_variables_from_expression(event_info["condition"]))
        for assignment in event_info["assignments"]:
            used_vars.update(_extract_variables_from_expression(assignment["expression"]))

    # Find unused variables
    unused_vars = defined_vars - used_vars

    return [f"Variable '{var}' is defined but never used" for var in unused_vars]


def _check_unused_inputs(model_structure: dict) -> list[str]:  # noqa: C901, PLR0912
    """Check for unused inputs."""

    # Get all defined inputs (safely handle missing keys)
    defined_inputs = set(model_structure.get("INPUTS", {}).keys())

    # Get all used inputs
    used_inputs = set()

    # Check usage in state equations
    for state_info in model_structure.get("STATES", {}).values():
        # Handle different model structure formats
        if isinstance(state_info, dict) and "expression" in state_info:
            expression = state_info["expression"]
        elif isinstance(state_info, str):
            expression = state_info
        else:
            continue
        used_inputs.update(_extract_variables_from_expression(expression))

    # Check usage in algebraic equations (for DAE models)
    alg_equations = model_structure.get("ALG_EQUATIONS", {})
    if isinstance(alg_equations, list):
        # DAE models have ALG_EQUATIONS as a list of expressions
        for alg_expr in alg_equations:
            used_inputs.update(_extract_variables_from_expression(alg_expr))
    elif isinstance(alg_equations, dict):
        # Some models might have ALG_EQUATIONS as a dict
        for alg_info in alg_equations.values():
            if isinstance(alg_info, dict) and "expression" in alg_info:
                used_inputs.update(_extract_variables_from_expression(alg_info["expression"]))
            elif isinstance(alg_info, str):
                used_inputs.update(_extract_variables_from_expression(alg_info))

    # Check usage in variables
    for var_info in model_structure.get("VARIABLES", {}).values():
        used_inputs.update(_extract_variables_from_expression(var_info["expression"]))

    # Check usage in features
    for feature_info in model_structure.get("FEATURES", {}).values():
        used_inputs.update(_extract_variables_from_expression(feature_info["expression"]))

    # Check usage in outputs
    for output_info in model_structure.get("OUTPUTS", {}).values():
        used_inputs.update(_extract_variables_from_expression(output_info["expression"]))

    # Check usage in events
    for event_info in model_structure.get("EVENTS", {}).values():
        used_inputs.update(_extract_variables_from_expression(event_info["condition"]))
        for assignment in event_info["assignments"]:
            used_inputs.update(_extract_variables_from_expression(assignment["expression"]))

    # Find unused inputs
    unused_inputs = defined_inputs - used_inputs

    return [f"Input '{input_name}' is defined but never used" for input_name in unused_inputs]


def _check_unused_parameters(model_structure: dict) -> list[str]:  # noqa: C901, PLR0912
    """Check for unused parameters."""

    # Get all defined parameters (safely handle missing keys)
    defined_params = set(model_structure.get("PARAMETERS", {}).keys())

    # Get all used parameters
    used_params = set()

    # Check usage in state equations
    for state_info in model_structure.get("STATES", {}).values():
        # Handle different model structure formats
        if isinstance(state_info, dict) and "expression" in state_info:
            expression = state_info["expression"]
        elif isinstance(state_info, str):
            expression = state_info
        else:
            continue
        used_params.update(_extract_variables_from_expression(expression))

    # Check usage in algebraic equations (for DAE models)
    alg_equations = model_structure.get("ALG_EQUATIONS", {})
    if isinstance(alg_equations, list):
        # DAE models have ALG_EQUATIONS as a list of expressions
        for alg_expr in alg_equations:
            used_params.update(_extract_variables_from_expression(alg_expr))
    elif isinstance(alg_equations, dict):
        # Some models might have ALG_EQUATIONS as a dict
        for alg_info in alg_equations.values():
            if isinstance(alg_info, dict) and "expression" in alg_info:
                used_params.update(_extract_variables_from_expression(alg_info["expression"]))
            elif isinstance(alg_info, str):
                used_params.update(_extract_variables_from_expression(alg_info))

    # Check usage in variables
    for var_info in model_structure.get("VARIABLES", {}).values():
        used_params.update(_extract_variables_from_expression(var_info["expression"]))

    # Check usage in features
    for feature_info in model_structure.get("FEATURES", {}).values():
        used_params.update(_extract_variables_from_expression(feature_info["expression"]))

    # Check usage in outputs
    for output_info in model_structure.get("OUTPUTS", {}).values():
        used_params.update(_extract_variables_from_expression(output_info["expression"]))

    # Check usage in events
    for event_info in model_structure.get("EVENTS", {}).values():
        used_params.update(_extract_variables_from_expression(event_info["condition"]))
        for assignment in event_info["assignments"]:
            used_params.update(_extract_variables_from_expression(assignment["expression"]))

    # Check usage in functions
    for func_info in model_structure.get("FUNCTIONS", {}).values():
        used_params.update(_extract_variables_from_expression(func_info["expression"]))

    # Find unused parameters
    unused_params = defined_params - used_params

    return [f"Parameter '{param}' is defined but never used" for param in unused_params]


def _check_undefined_dependencies(model_structure: dict) -> list[str]:
    """Check for features depending on undefined variables/states/parameters."""
    errors = []

    # Get all defined symbols (safely handle missing keys)
    defined_symbols = set()
    defined_symbols.update(model_structure.get("STATES", {}).keys())
    defined_symbols.update(model_structure.get("PARAMETERS", {}).keys())
    defined_symbols.update(model_structure.get("VARIABLES", {}).keys())
    defined_symbols.update(model_structure.get("INPUTS", {}).keys())
    defined_symbols.update(model_structure.get("FUNCTIONS", {}).keys())
    defined_symbols.update(
        model_structure.get("OUTPUTS", {}).keys(),
    )  # Add outputs to defined symbols
    defined_symbols.add("time")  # time is always available

    # Add predefined mathematical constants
    predefined_constants = {
        "CONSTANT_E",
        "CONSTANT_LOG2_E",
        "CONSTANT_LOG10_E",
        "CONSTANT_PI",
        "CONSTANT_INV_PI",
        "CONSTANT_INV_SQRT_PI",
        "CONSTANT_LN_2",
        "CONSTANT_LN_10",
        "CONSTANT_SQRT_2",
        "CONSTANT_SQRT_3",
        "CONSTANT_INV_SQRT_3",
        "CONSTANT_GAMMA",
        "CONSTANT_PHI",
    }
    defined_symbols.update(predefined_constants)

    # Check features
    for feature_name, feature_info in model_structure.get("FEATURES", {}).items():
        referenced_vars = _extract_variables_from_expression(feature_info["expression"])
        undefined_vars = referenced_vars - defined_symbols

        errors.extend(
            [
                f"Feature '{feature_name}' depends on undefined variable '{var}'"
                for var in undefined_vars
            ],
        )

    # Check outputs
    for output_name, output_info in model_structure.get("OUTPUTS", {}).items():
        referenced_vars = _extract_variables_from_expression(output_info["expression"])
        undefined_vars = referenced_vars - defined_symbols

        errors.extend(
            [
                f"Output '{output_name}' depends on undefined variable '{var}'"
                for var in undefined_vars
            ],
        )

    # Check variables
    for var_name, var_info in model_structure.get("VARIABLES", {}).items():
        referenced_vars = _extract_variables_from_expression(var_info["expression"])
        # Remove self-reference
        referenced_vars.discard(var_name)
        undefined_vars = referenced_vars - defined_symbols

        errors.extend(
            [
                f"Variable '{var_name}' depends on undefined variable '{var}'"
                for var in undefined_vars
            ],
        )

    return errors


def _check_negative_signs(model_structure: dict) -> list[str]:
    """Check for negative signs in variables/reactions (discouraged)."""
    warnings_list = []

    # Check variables (safely handle missing keys)
    for var_name, var_info in model_structure.get("VARIABLES", {}).items():
        expression = var_info["expression"]
        if _has_leading_negative_sign(expression):
            warnings_list.append(
                f"Variable '{var_name}' has negative sign in expression: '{expression}' - consider using positive formulation",  # noqa: E501
            )

    return warnings_list


def _check_duplicate_usage_in_derivatives(model_structure: dict) -> list[str]:
    """Check for parameters used in chained multiplication through variable substitution."""
    warnings_list = []

    # Get variable definitions for substitution
    variables = model_structure.get("VARIABLES", {})

    # Check each state derivative
    for state_name, state_info in model_structure.get("STATES", {}).items():
        # Handle different model structure formats
        if isinstance(state_info, dict) and "expression" in state_info:
            original_expression = state_info["expression"]
        elif isinstance(state_info, str):
            original_expression = state_info
        else:
            continue

        # Get variables used directly in the derivative
        direct_vars = _extract_variables_from_expression(original_expression)

        # For each variable used in the derivative,
        # check if substituting it creates chained multiplication
        for var_name in direct_vars:
            if var_name in variables:
                var_expr = variables[var_name].get("expression", "")
                if not var_expr:
                    continue

                # Check if this variable appears in multiplication with parameters
                # that are also in the variable
                chained_params = _find_chained_multiplication_params(
                    original_expression,
                    var_name,
                    var_expr,
                )

                warnings_list.extend(
                    [
                        f"Parameter '{param}' appears in chained operations in state derivative {state_name} (through variable '{var_name}' which also contains '{param}')"  # noqa: E501
                        for param in chained_params
                    ],
                )

    return warnings_list


def _find_chained_multiplication_params(
    derivative_expr: str,
    var_name: str,
    var_expr: str,
) -> set[str]:
    """
    Find parameters that appear in chained multiplication/division through variable substitution.
    """

    # Get parameters in the variable expression
    var_params = _extract_variables_from_expression(var_expr)

    # Find terms that contain the variable
    # Split by + and - to get individual terms
    terms = re.split(r"\s*[+-]\s*", derivative_expr)

    chained_params = set()

    for term in terms:
        if var_name in term:
            # Get all parameters in this term
            term_params = _extract_variables_from_expression(term)
            term_params.discard(var_name)  # Remove the variable itself

            # Check if any parameter in this term is also in the variable expression
            common_params = term_params & var_params

            if common_params:
                # Check for problematic chaining patterns
                for param in common_params:
                    if _is_problematic_chaining(term, var_expr, param):
                        chained_params.add(param)

    return chained_params


def _is_problematic_chaining(term: str, var_expr: str, param: str) -> bool:
    """Check if a parameter creates problematic chaining in a term."""

    # Check multiplication/division patterns in the term and variable expression
    param_in_term_mult = _count_param_in_multiplication(term, param)
    param_in_term_div = _count_param_in_division(term, param)
    param_in_var_mult = _count_param_in_multiplication(var_expr, param)
    param_in_var_div = _count_param_in_division(var_expr, param)

    # Problematic cases:
    # 1. Both multiplication: param * (param * ...) -> param^2
    # 2. Both division: param / (... / param) -> param^2
    # 3. Division by division: (... / param) / param -> 1/param^2

    # Case 1: Multiplication chaining (param^2 or higher)
    if param_in_term_mult > 0 and param_in_var_mult > 0:
        return True

    # Case 2: Division chaining that creates param^2 in denominator
    if param_in_term_div > 0 and param_in_var_div > 0:
        return True

    # Case 3: Mixed cases that don't cancel out nicely
    # For now, we'll be conservative and only flag clear multiplicative/division chaining
    # Mixed multiplication/division often cancels out (k2 * B/k2 = B)

    return False


def _count_param_in_multiplication(expression: str, param: str) -> int:
    """Count how many times a parameter appears in multiplicative context."""

    # Look for param followed by * or preceded by *
    mult_patterns = [
        rf"\b{re.escape(param)}\s*\*",  # param *
        rf"\*\s*{re.escape(param)}\b",  # * param
        rf"^\s*{re.escape(param)}\s*\*",  # param at start followed by *
        rf"\*\s*{re.escape(param)}\s*$",  # * param at end
    ]

    count = 0
    for pattern in mult_patterns:
        if re.search(pattern, expression):
            count += 1
            break  # Don't double count the same occurrence

    return count


def _count_param_in_division(expression: str, param: str) -> int:
    """Count how many times a parameter appears in division context."""

    # Look for param in division context
    div_patterns = [
        rf"\b{re.escape(param)}\s*/",  # param /
        rf"/\s*{re.escape(param)}\b",  # / param
        rf"^\s*{re.escape(param)}\s*/",  # param at start followed by /
        rf"/\s*{re.escape(param)}\s*$",  # / param at end
    ]

    count = 0
    for pattern in div_patterns:
        if re.search(pattern, expression):
            count += 1
            break  # Don't double count the same occurrence

    return count


def _expand_expression(expression: str, variables: dict[str, dict]) -> str:
    """Expand an expression by substituting variable definitions recursively."""
    if not expression or not variables:
        return expression

    # Make a copy to avoid modifying the original
    expanded = expression

    # Keep track of substitutions to avoid infinite recursion
    substituted = set()
    max_iterations = len(variables) + 5  # Safety limit
    iterations = 0

    while iterations < max_iterations:
        old_expanded = expanded

        # Try to substitute each variable
        for var_name, var_info in variables.items():
            if var_name in substituted:
                continue

            var_expression = var_info.get("expression", "")
            if not var_expression:
                continue

            # Look for the variable in the expanded expression
            # Use word boundaries to avoid partial matches
            pattern = rf"\b{re.escape(var_name)}\b"

            if re.search(pattern, expanded):
                # Substitute the variable with its expression (wrapped in parentheses for safety)
                expanded = re.sub(pattern, f"({var_expression})", expanded)
                substituted.add(var_name)

        iterations += 1

        # If no changes were made, we're done
        if expanded == old_expanded:
            break

    return expanded


def _count_parameter_usage(expression: str) -> dict[str, int]:
    """Count how many times each parameter/variable appears in an expression."""
    if not expression:
        return {}

    # Extract all parameter/variable names from the expression
    variables = _extract_variables_from_expression(expression)

    # Count occurrences of each variable
    counts = {}

    for var_name in variables:
        if var_name:
            # Count occurrences using word boundaries
            pattern = rf"\b{re.escape(var_name)}\b"
            count = len(re.findall(pattern, expression))
            if count > 0:
                counts[var_name] = count

    return counts


def _looks_like_rate_parameter(param_name: str, state_name: str) -> bool:
    """Check if parameter name suggests it's a rate parameter related to a specific state."""
    param_lower = param_name.lower()
    state_lower = state_name.lower()

    # Check for patterns like kA for state A, vA for state A, etc.
    rate_patterns = [
        f"k{state_lower}",
        f"v{state_lower}",
        f"{state_lower}_rate",
        f"rate_{state_lower}",
        f"k_{state_lower}",
        f"v_{state_lower}",
    ]

    return param_lower in rate_patterns


def _check_additional_issues(model_structure: dict) -> tuple[list[str], list[str]]:
    """Check for additional model issues."""
    errors = []
    warnings_list = []

    # Check for empty sections (safely handle missing keys)
    if not model_structure.get("STATES", {}):
        errors.append("Model has no states defined")

    if not model_structure.get("FEATURES", {}):
        warnings_list.append("Model has no features defined")

    # Check for inconsistent naming (states vs parameters vs variables)
    naming_issues = _check_naming_consistency(model_structure)
    warnings_list.extend(naming_issues)

    return errors, warnings_list


def _extract_variables_from_expression(expression: str) -> set[str]:
    """Extract variable names from an expression."""
    if not expression:
        return set()

    # Find all potential variable names (word characters, possibly with colons for containers)
    # Exclude function calls (followed by parentheses)
    variables = set()

    # Pattern to match variable names, optionally with container prefix
    pattern = r":?\b[a-zA-Z_][a-zA-Z0-9_:]*\b(?!\s*\()"
    matches = re.findall(pattern, expression)

    for match in matches:
        # Filter out common mathematical constants and functions
        if match.lower() not in [
            "pi",
            "e",
            "sin",
            "cos",
            "tan",
            "log",
            "exp",
            "sqrt",
            "abs",
            "min",
            "max",
            "pow",
        ]:
            variables.add(match)

    return variables


def _looks_like_rate_variable(var_name: str) -> bool:
    """Check if variable name suggests it's a rate variable."""
    rate_patterns = [
        r".*rate.*",
        r"v[0-9]+",  # v1, v2, etc.
        r"v[A-Z][a-zA-Z0-9_]*",  # vA, vB, etc.
        r"k[0-9]+",  # k1, k2, etc.
        r"k[A-Z][a-zA-Z0-9_]*",  # kA, kB, etc.
        r".*_rate",
        r"rate_.*",
    ]

    return any(re.match(pattern, var_name, re.IGNORECASE) for pattern in rate_patterns)


def _guess_state_from_rate_name(var_name: str) -> str | None:
    """Try to guess which state a rate variable might be for."""
    # Common patterns
    patterns = [
        (r"v([A-Z][a-zA-Z0-9_]*)", r"\1"),  # vA -> A
        (r"k([A-Z][a-zA-Z0-9_]*)", r"\1"),  # kA -> A
        (r"([A-Z][a-zA-Z0-9_]*)_rate", r"\1"),  # A_rate -> A
        (r"rate_([A-Z][a-zA-Z0-9_]*)", r"\1"),  # rate_A -> A
    ]

    for pattern, _replacement in patterns:
        match = re.match(pattern, var_name)
        if match:
            return match.group(1)

    return None


def _has_leading_negative_sign(expression: str) -> bool:
    """Check if expression has a leading negative sign."""
    expr = expression.strip()
    return expr.startswith("-") and not expr.startswith("--")


def _has_negative_terms(expression: str) -> bool:
    """Check if expression contains negative terms."""
    if not expression:
        return False

    # Simple check for negative signs (not at the beginning of the expression)
    # This looks for patterns like: "something - something" or "- k1" etc.
    expr = expression.strip()

    # Check for leading negative sign
    if expr.startswith("-"):
        return True

    # Check for negative terms in the middle (preceded by space or operator)
    # Look for - signs that are not part of numbers or at the start
    negative_pattern = r"(?:^|\s|[+*/()])\s*-\s*[a-zA-Z_]"
    return bool(re.search(negative_pattern, expr))


def _looks_like_constant_degradation(expression: str) -> bool:
    """Check if expression looks like a constant degradation rate."""
    # Remove whitespace
    expr = _remove_white_space(expression)

    # Check for patterns like: -k1, -0.5, -k1*2, etc.
    # These are constant degradation rates that don't depend on the state
    simple_negative_pattern = (
        r"^-[a-zA-Z_][a-zA-Z0-9_]*(\*[0-9.]+)?$|^-[0-9.]+(\*[a-zA-Z_][a-zA-Z0-9_]*)?$|^-[0-9.]+$"
    )

    return bool(re.match(simple_negative_pattern, expr))


def _check_naming_consistency(model_structure: dict) -> list[str]:
    """Check for naming consistency issues."""
    warnings_list = []

    # Get all names (safely handle missing keys)
    state_names = set(model_structure.get("STATES", {}).keys())
    param_names = set(model_structure.get("PARAMETERS", {}).keys())
    var_names = set(model_structure.get("VARIABLES", {}).keys())
    input_names = set(model_structure.get("INPUTS", {}).keys())

    # Check for name conflicts
    all_names = [
        ("states", state_names),
        ("parameters", param_names),
        ("variables", var_names),
        ("inputs", input_names),
    ]

    for i, (type1, names1) in enumerate(all_names):
        for j, (type2, names2) in enumerate(all_names):
            if i < j:  # Only check each pair once
                conflicts = names1 & names2
                warnings_list.extend(
                    [f"Name '{name}' is used in both {type1} and {type2}" for name in conflicts],
                )

    return warnings_list


def print_validation_results(results: dict[str, list[str]], model_name: str = "model") -> None:
    """Log validation results in a formatted way (backwards compatible name)."""
    errors = results["errors"]
    warnings = results["warnings"]

    if not errors and not warnings:
        logger.info("Model '%s' passed all validation checks!", model_name)
        return

    logger.info("Validation results for model '%s':", model_name)
    logger.info("%s", "=" * 50)

    if errors:
        logger.error(" ERRORS (%d):", len(errors))
        for i, error in enumerate(errors, 1):
            logger.error("  %d. %s", i, error)

    if warnings:
        logger.warning(" WARNINGS (%d):", len(warnings))
        for i, warning in enumerate(warnings, 1):
            logger.warning("  %d. %s", i, warning)

    logger.info("%s", "=" * 50)
    logger.info("Summary: %d errors, %d warnings", len(errors), len(warnings))


def _is_variable_used_negatively(var_name: str, expression: str) -> bool:
    """Check if a variable is used in a negative context in an expression."""
    if not expression or not var_name:
        return False

    # Look for patterns like: -var_name, - var_name, etc.
    # Pattern to match negative usage of the variable
    # This looks for the variable name preceded by a minus sign
    negative_pattern = rf"(?:^|\s|[+*/\(])\s*-\s*{re.escape(var_name)}\b"

    return bool(re.search(negative_pattern, expression))
