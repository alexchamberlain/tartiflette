from functools import partial
from typing import Any, Callable, Dict, List, Optional, Union


async def default_argument_execution_directive(
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


async def default_directive_callable(value: Any, *args, **kwargs) -> Any:
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
    "on_argument_execution": default_argument_execution_directive
}


async def directive_executor(
    directive_func: Callable,
    directive_args: Union[Dict[str, Any], Callable],
    wrapped_func: Callable,
    *args,
    **kwargs,
) -> Any:
    """
    TODO:
    :param directive_func: TODO:
    :param directive_args: TODO:
    :param wrapped_func: TODO:
    :param args: TODO:
    :param kwargs: TODO:
    :type directive_func: TODO:
    :type directive_args: TODO:
    :type wrapped_func: TODO:
    :type args: TODO:
    :type kwargs: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return await directive_func(
        await directive_args() if callable(directive_args) else directive_args,
        wrapped_func,
        *args,
        **kwargs,
    )


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
            directive_hook, default_directive_callable
        )

    for directive in reversed(directives_definition):
        if directive_hook in directive["callables"]:
            func = partial(
                directive_executor,
                directive["callables"][directive_hook],
                directive["args"],
                func,
            )
    return func
