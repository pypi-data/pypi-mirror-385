import warnings

def check_return_results(return_list: list[str], callable_names: list[str], callable_type: str) -> None:
    """
    Validates and warns about the order of user-requested workflow/method/module outputs.

    :param return_list: The list of callables to be returned (e.g., return_workflows).
    :param callable_names: The names of callables in the pipeline, in execution order.
    :param callable_type: The kind of callable being validated (e.g., 'workflow', 'method', 'module').
    """

    callables: set[str] = set(callable_names)

    invalid_callables = [name for name in return_list if name not in callables]

    if invalid_callables:
        raise ValueError(f"The provided {callable_type}s do not include the following {callable_type}(s): {', '.join(invalid_callables)}")

    actual_order = [name for name in callable_names if name in return_list]

    if actual_order != return_list:
        warnings.warn(f"The {callable_type}s will be returned in the execution order ({actual_order}) not in the order you provided ({return_list}). Be careful when unpacking the results", stacklevel=3)