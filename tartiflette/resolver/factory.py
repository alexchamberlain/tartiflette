from functools import partial
from typing import Any, Callable, List, Optional, Union

from tartiflette.execution.types import build_resolve_info
from tartiflette.resolver.default import default_field_resolver
from tartiflette.types.helpers.get_directive_instances import (
    get_query_directive_instances,
)
from tartiflette.utils.coercer_way import CoercerWay
from tartiflette.utils.directives import wraps_with_directives
from tartiflette.utils.errors import located_error


def handle_field_error(
    raw_error: Exception,
    field_nodes: List["FieldNode"],
    path: "Path",
    return_type: "GraphQLOutputType",
    execution_context: "ExecutionContext",
) -> None:
    """
    TODO:
    :param raw_error: TODO:
    :param field_nodes: TODO:
    :param path: TODO:
    :param return_type: TODO:
    :param execution_context: TODO:
    :type raw_error: TODO:
    :type field_nodes: TODO:
    :type path: TODO:
    :type return_type: TODO:
    :type execution_context: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # TODO: tmp fix for cyclic imports
    from tartiflette.types.helpers.definition import is_non_null_type

    error = located_error(raw_error, field_nodes, path.as_list())

    # If the field type is non-nullable, then it is resolved without any
    # protection from errors, however it still properly locates the error.
    if is_non_null_type(return_type):
        raise error

    # Otherwise, error protection is applied, logging the error and resolving
    # a null value for this field if one is encountered.
    # TODO: not the best way to handle it since path on non null return type
    # will  not be the good one
    execution_context.add_error(error)
    return None


async def complete_value_catching_error(
    execution_context: "ExecutionContext",
    field_nodes: List["FieldNode"],
    info: "ResolveInfo",
    path: "Path",
    result: Any,
    output_coercer: Callable,
    return_type: "GraphQLOutputType",
) -> Any:
    """
    TODO:
    :param execution_context: TODO:
    :param field_nodes: TODO:
    :param info: TODO:
    :param path: TODO:
    :param result: TODO:
    :param output_coercer: TODO:
    :param return_type: TODO:
    :type execution_context: TODO:
    :type field_nodes: TODO:
    :type info: TODO:
    :type path: TODO:
    :type result: TODO:
    :type output_coercer: TODO:
    :type return_type: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    try:
        if isinstance(result, Exception):
            raise result

        return await output_coercer(
            result=result,
            execution_context=execution_context,
            field_nodes=field_nodes,
            info=info,
            path=path,
        )
    except Exception as raw_exception:  # pylint: disable=broad-except
        return handle_field_error(
            raw_exception, field_nodes, path, return_type, execution_context
        )


async def resolve_field_value_or_error(
    execution_context: "ExecutionContext",
    field_definition: "GraphQLField",
    field_nodes: List["FieldNode"],
    resolver: Callable,
    source: Any,
    info: "ResolveInfo",
) -> Union[Exception, Any]:
    """
    TODO:
    :param execution_context: TODO:
    :param field_definition: TODO:
    :param field_nodes: TODO:
    :param resolver: TODO:
    :param source: TODO:
    :param info: TODO:
    :type execution_context: TODO:
    :type field_definition: TODO:
    :type field_nodes: TODO:
    :type resolver: TODO:
    :type source: TODO:
    :type info: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # TODO: tmp fix for cyclic imports
    from tartiflette.coercers.arguments import coerce_arguments
    from tartiflette.types.helpers.definition import get_wrapped_type

    try:
        computed_directives = []
        for field_node in field_nodes:
            computed_directives.extend(
                get_query_directive_instances(
                    execution_context, field_node.directives, info
                )
            )

        resolver = wraps_with_directives(
            directives_definition=computed_directives,
            directive_hook="on_field_execution",
            func=resolver,
        )

        result = await resolver(
            source,
            await coerce_arguments(
                field_definition.arguments,
                field_nodes[0],
                execution_context.variable_values,
                execution_context.context,
                info,
            ),
            execution_context.context,
            info,
        )

        # TODO: refactor this :)
        if not isinstance(result, Exception):
            rtype = get_wrapped_type(field_definition.graphql_type)
            if hasattr(rtype, "directives"):
                directives = rtype.directives.get(CoercerWay.OUTPUT)
                result = await directives(
                    result, field_definition, execution_context.context, info
                )
        return result
    except Exception as e:  # pylint: disable=broad-except
        return e


async def resolve_field(
    execution_context: "ExecutionContext",
    parent_type: "GraphQLObjectType",
    source: Any,
    field_nodes: List["FieldNode"],
    path: "Path",
    field_definition: "GraphQLField",
    resolver: Callable,
    output_coercer: Callable,
) -> Any:
    """
    TODO:
    :param execution_context: TODO:
    :param parent_type: TODO:
    :param source: TODO:
    :param field_nodes: TODO:
    :param path: TODO:
    :param field_definition: TODO:
    :param resolver: TODO:
    :param output_coercer: TODO:
    :type execution_context: TODO:
    :type parent_type: TODO:
    :type source: TODO:
    :type field_nodes: TODO:
    :type path: TODO:
    :type field_definition: TODO:
    :type resolver: TODO:
    :type output_coercer: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    info = build_resolve_info(
        execution_context, field_definition, field_nodes, parent_type, path
    )

    result = await resolve_field_value_or_error(
        execution_context,
        field_definition,
        field_nodes,
        resolver,
        source,
        info,
    )

    return await output_coercer(
        execution_context, field_nodes, info, path, result
    )


def get_field_resolver(
    field_definition: "GraphQLField",
    custom_default_resolver: Optional[Callable],
) -> Callable:
    """
    TODO:
    :param field_definition: TODO:
    :param custom_default_resolver: TODO:
    :type field_definition: TODO:
    :type custom_default_resolver: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # TODO: tmp fix for cyclic imports
    from tartiflette.coercers.output import get_output_coercer

    resolver = wraps_with_directives(
        directives_definition=field_definition.directives_definition,
        directive_hook="on_field_execution",
        func=(
            field_definition.raw_resolver
            or custom_default_resolver
            or default_field_resolver
        ),
    )

    return_type = field_definition.graphql_type

    return partial(
        resolve_field,
        field_definition=field_definition,
        resolver=resolver,
        output_coercer=partial(
            complete_value_catching_error,
            output_coercer=get_output_coercer(
                return_type, field_definition.type_resolver
            ),
            return_type=return_type,
        ),
    )
