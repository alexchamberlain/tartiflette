from functools import partial
from typing import Any, Callable, Dict, List, Optional


async def _default_argument_execution_directive(
    argument_definition: "GraphQLArgument", value: Any, *args, **kwargs
) -> Any:
    """
    Default callable to use to wrap with directives on `on_argument_execution`
    hook name.
    :param argument_definition: the GraphQLArgument instance of the argument
    :param value: the coerced value of the argument
    :type argument_definition: GraphQLArgument
    :type value: Any
    :return: the coerced value of the argument
    :rtype: Any
    """
    # pylint: disable=unused-argument
    return value


async def _default_directive_callable(value: Any, *args, **kwargs) -> Any:
    """
    Default callable to use to wrap with directives when the hook doesn't
    implements a specific callable.
    :param value: the coerced value
    :type value: Any
    :return: the coerced value
    :rtype: Any
    """
    # pylint: disable=unused-argument
    return value


_DEFAULT_HOOKS_CALLABLE = {
    "on_argument_execution": _default_argument_execution_directive
}


def wraps_with_directives(
    directives_definition: List[Dict[str, Any]],
    directive_hook: str,
    func: Optional[Callable] = None,
) -> Callable:
    """
    Wraps a callable with directives.
    :param directives_definition: directives to wrap with
    :param directive_hook: name of the hook to wrap with
    :param func: callable to wrap
    :type directives_definition: List[Dict[str, Any]]
    :type directive_hook: str
    :type func: Optional[Callable]
    :return: wrapped callable
    :rtype: Callable
    """
    if func is None:
        func = _DEFAULT_HOOKS_CALLABLE.get(
            directive_hook, _default_directive_callable
        )

    for directive in reversed(directives_definition):
        if directive_hook in directive["callables"]:
            func = partial(
                directive["callables"][directive_hook], directive["args"], func
            )
    return func
