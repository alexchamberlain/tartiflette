from functools import partial, wraps
from typing import Any, Callable, Dict, List, Optional, Union

from tartiflette.coercers.common import Path
from tartiflette.execution.collect import collect_subfields
from tartiflette.execution.execute import execute_fields
from tartiflette.resolver.default import default_type_resolver
from tartiflette.resolver.factory import complete_value_catching_error
from tartiflette.types.helpers.definition import (
    get_wrapped_type,
    is_abstract_type,
    is_leaf_type,
    is_list_type,
    is_non_null_type,
    is_object_type,
    is_wrapping_type,
)
from tartiflette.utils.directives import wraps_with_directives
from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.utils.values import is_invalid_value


def ensure_valid_runtime_type(
    runtime_type_or_name: Union["GraphQLObjectType", str],
    execution_context: "ExecutionContext",
    return_type: "GraphQLAbstractType",
    field_nodes: List["FieldNodes"],
    info: "ResolveInfo",
    result: Any,
) -> "GraphQLObjectType":
    """
    TODO:
    :param runtime_type_or_name: TODO:
    :param execution_context: TODO:
    :param return_type: TODO:
    :param field_nodes: TODO:
    :param info: TODO:
    :param result: TODO:
    :type runtime_type_or_name: TODO:
    :type execution_context: TODO:
    :type return_type: TODO:
    :type field_nodes: TODO:
    :type info: TODO:
    :type result: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    runtime_type = (
        execution_context.schema.find_type(runtime_type_or_name)
        if isinstance(runtime_type_or_name, str)
        else runtime_type_or_name
    )

    if not is_object_type(runtime_type):
        raise graphql_error_from_nodes(
            f"Abstract type {return_type.name} must resolve to an Object type "
            "at runtime for field "
            f"{info.parent_type.name}.{info.field_name} with value "
            f'{type(result)}, received "{runtime_type}".'
            f"Either the {return_type.name} type should provide a "
            f'"resolveType" function or each possible type should provide '
            'an "isTypeOf" function.',
            nodes=field_nodes,
        )

    if not return_type.is_possible_type(runtime_type):
        raise graphql_error_from_nodes(
            f"Runtime Object type < {runtime_type.name} > is not a possible "
            f"type for < {return_type.name} >.",
            nodes=field_nodes,
        )
    return runtime_type


async def complete_object_value(
    execution_context: "ExecutionContext",
    return_type: "GraphQLOuputType",
    field_nodes: List["FieldNode"],
    info: "ResolveInfo",
    path: "Path",
    result: Any,
):
    """
    Complete an Object value by executing all sub-selections.
    :param execution_context: TODO:
    :param return_type: TODO:
    :param field_nodes: TODO:
    :param info: TODO:
    :param path: TODO:
    :param result: TODO:
    :type execution_context: TODO:
    :type return_type: TODO:
    :type field_nodes: TODO:
    :type info: TODO:
    :type path: TODO:
    :type result: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # pylint: disable=unused-argument
    # TODO: `isTypeOf` WTF?
    return await execute_fields(
        execution_context,
        return_type,
        result,
        path,
        await collect_subfields(execution_context, return_type, field_nodes),
    )


def null_coercer_wrapper(coercer: Callable) -> Any:
    """
    TODO:
    :param coercer: TODO:
    :type coercer: TODO:
    :return: TODO:
    :rtype: TODO:
    """

    @wraps(coercer)
    async def wrapper(result, *args, **kwargs):
        if result is None:
            return None
        return await coercer(result, *args, **kwargs)

    return wrapper


@null_coercer_wrapper
async def leaf_coercer(
    result: Any,
    leaf_type: Union["GraphQLScalar", "GraphQLEnumType"],
    *args,
    **kwargs,
) -> Any:
    """
    TODO:
    :param result: TODO:
    :param leaf_type: TODO:
    :type result: TODO:
    :type leaf_type: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    coerced_result = leaf_type.coerce_output(result)
    if is_invalid_value(coerced_result):
        raise ValueError(
            f"Expected value of type {leaf_type} but received {type(result)}."
        )
    return coerced_result


@null_coercer_wrapper
async def abstract_coercer(
    result: Any,
    abstract_type: "GraphQLAbstractType",
    type_resolver: Optional[Callable],
    execution_context: "ExecutionContext",
    field_nodes: List["FieldNode"],
    info: "ResolveInfo",
    path: "Path",
    *args,
    **kwargs,
) -> Dict[str, Any]:
    """
    TODO:
    :param result: TODO:
    :param abstract_type: TODO:
    :param execution_context: TODO:
    :param field_nodes: TODO:
    :param info: TODO:
    :param path: TODO:
    :type result: TODO:
    :type abstract_type: TODO:
    :type execution_context: TODO:
    :type field_nodes: TODO:
    :type info: TODO:
    :type path: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    if type_resolver is None:
        type_resolver = default_type_resolver

    return await complete_object_value(
        execution_context,
        ensure_valid_runtime_type(
            await type_resolver(
                result, execution_context.context, info, abstract_type
            ),
            execution_context,
            abstract_type,
            field_nodes,
            info,
            result,
        ),
        field_nodes,
        info,
        path,
        result,
    )


@null_coercer_wrapper
async def object_coercer(
    result: Any,
    object_type: "GraphQLObjectType",
    execution_context: "ExecutionContext",
    field_nodes: List["FieldNode"],
    info: "ResolveInfo",
    path: "Path",
    *args,
    **kwargs,
) -> Dict[str, Any]:
    """
    TODO:
    :param result: TODO:
    :param object_type: TODO:
    :param execution_context: TODO:
    :param field_nodes: TODO:
    :param info: TODO:
    :param path: TODO:
    :type result: TODO:
    :type object_type: TODO:
    :type execution_context: TODO:
    :type field_nodes: TODO:
    :type info: TODO:
    :type path: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return await complete_object_value(
        execution_context, object_type, field_nodes, info, path, result
    )


@null_coercer_wrapper
async def list_coercer(
    result: Any,
    inner_coercer: Callable,
    item_type: "GraphQLOuputType",
    execution_context: "ExecutionContext",
    field_nodes: List["FieldNode"],
    info: "ResolveInfo",
    path: "Path",
    *args,
    **kwargs,
) -> List[Any]:
    """
    TODO:
    :param result: TODO:
    :param inner_coercer: TODO:
    :param item_type: TODO:
    :param execution_context: TODO:
    :param field_nodes: TODO:
    :param info: TODO:
    :param path: TODO:
    :type result: TODO:
    :type inner_coercer: TODO:
    :type item_type: TODO:
    :type execution_context: TODO:
    :type field_nodes: TODO:
    :type info: TODO:
    :type path: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    if not isinstance(result, list):
        raise TypeError(
            "Expected Iterable, but did not find one for field "
            f"{info.parent_type.name}.{info.field_name}."
        )

    # TODO: should we gather this?
    return [
        await complete_value_catching_error(
            execution_context,
            field_nodes,
            info,
            Path(path, index),
            item,
            inner_coercer,
            item_type,
        )
        for index, item in enumerate(result)
    ]


async def non_null_coercer(
    result: Any, inner_coercer: Callable, *args, **kwargs
) -> Any:
    """
    TODO:
    :param result: TODO:
    :param inner_coercer: TODO:
    :type result: TODO:
    :type inner_coercer: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    coerced_output = await inner_coercer(result, *args, **kwargs)
    if coerced_output is None:
        info = kwargs["info"]  # TODO: refactor this...
        raise ValueError(
            "Cannot return null for non-nullable field "
            f"{info.parent_type.name}.{info.field_name}."
        )
    return coerced_output


def get_output_coercer(
    schema_type: "GraphQLType", type_resolver: Optional[Callable]
) -> Callable:
    """
    TODO:
    :param schema_type: TODO:
    :param type_resolver: TODO:
    :type schema_type: TODO:
    :type type_resolver: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    wrapped_type = get_wrapped_type(schema_type)

    wrapped_type_directives = (
        getattr(wrapped_type, "directives_definition", None) or []
    )

    if is_leaf_type(wrapped_type):
        coercer = partial(leaf_coercer, leaf_type=wrapped_type)
    elif is_abstract_type(wrapped_type):
        coercer = partial(
            abstract_coercer,
            abstract_type=wrapped_type,
            type_resolver=type_resolver,
        )
    elif is_object_type(wrapped_type):
        coercer = partial(object_coercer, object_type=wrapped_type)
    else:
        coercer = lambda *args, **kwargs: None  # Not a valid type anyway...

    if wrapped_type_directives:
        directives = wraps_with_directives(
            directives_definition=wrapped_type_directives,
            directive_hook="on_pre_output_coercion",
        )
        if directives:
            pass

    inner_type = schema_type
    wrapper_coercers = []
    while is_wrapping_type(inner_type):
        wrapped_type = inner_type.wrapped_type
        if is_list_type(inner_type):
            wrapper_coercers.append(
                partial(list_coercer, item_type=wrapped_type)
            )
        elif is_non_null_type(inner_type):
            wrapper_coercers.append(non_null_coercer)
        inner_type = wrapped_type

    for wrapper_coercer in reversed(wrapper_coercers):
        coercer = partial(wrapper_coercer, inner_coercer=coercer)

    return coercer
