import asyncio

from typing import Any, Callable, Dict, List, Optional, Union

from tartiflette.constants import UNDEFINED_VALUE
from tartiflette.language.ast import NullValueNode, VariableNode
from tartiflette.types.exceptions.tartiflette import MultipleException
from tartiflette.types.helpers.definition import is_non_null_type
from tartiflette.utils.errors import graphql_error_from_nodes, located_error
from tartiflette.utils.values import is_invalid_value


async def argument_coercer(
    argument_definition: "GraphQLArgument",
    node: Union["FieldNode", "DirectiveNode"],
    argument_node: Optional["ArgumentNode"],
    variable_values: Dict[str, Any],
    ctx: Optional[Any],
    info: Optional["Info"],
    directives: Callable,
) -> Any:
    """
    Computes the value of an argument.
    :param argument_definition: the argument definition to treat
    :param node: TODO:
    :param argument_node: TODO:
    :param variable_values: the variables used in the GraphQL request
    :param ctx: context passed to the query execution
    :param info: information related to the execution and the resolved field
    :param directives: the directives to execute
    :type argument_definition: GraphQLArgument
    :type node: TODO:
    :type argument_node: TODO:
    :type variable_values: Dict[str, Any]
    :type ctx: Optional[Any]
    :type info: Optional[Info]
    :type directives: Callable
    :return: the computed value
    :rtype: Any
    """
    # pylint: disable=too-many-locals
    name = argument_definition.name
    arg_type = argument_definition.graphql_type

    if argument_node and isinstance(argument_node.value, VariableNode):
        variable_name = argument_node.value.name.value
        has_value = variable_values and variable_name in variable_values
        is_null = has_value and variable_values[variable_name] is None
    else:
        has_value = argument_node is not None
        is_null = argument_node and isinstance(
            argument_node.value, NullValueNode
        )

    coerced_value = UNDEFINED_VALUE
    if not has_value and argument_definition.default_value is not None:
        # TODO: we should coerce `argument_definition.default_value` to
        # apply directives on it. We can't do it for now since
        # `argument_definition.default_value` is an hard coded value filled
        # in the GraphQLArgument instance and not an AST ValueNode.
        # This will be possible when the GraphQLSchema will be build
        # via a DocumentNode.
        coerced_value = argument_definition.default_value
    elif (not has_value or is_null) and is_non_null_type(arg_type):
        if is_null:
            raise graphql_error_from_nodes(
                f"Argument < {name} > of non-null type < {arg_type} > "
                "must not be null.",
                nodes=argument_node.value,
            )
        if argument_node and isinstance(argument_node.value, VariableNode):
            raise graphql_error_from_nodes(
                f"Argument < {name} > of required type < {arg_type} > "
                f"was provided the variable < ${variable_name} > which "
                "was not provided a runtime value.",
                nodes=argument_node.value,
            )
        raise graphql_error_from_nodes(
            f"Argument < {name} > of required type < {arg_type} > was "
            "not provided.",
            nodes=node,
        )
    elif has_value:
        if isinstance(argument_node.value, NullValueNode):
            coerced_value = None
        elif isinstance(argument_node.value, VariableNode):
            variable_name = argument_node.value.name.value
            coerced_value = variable_values[variable_name]
        else:
            value_node = argument_node.value
            coerced_value = await argument_definition.literal_coercer(
                value_node, variables=variable_values
            )
            if is_invalid_value(coerced_value):
                raise graphql_error_from_nodes(
                    f"Argument < {name} > has invalid value "
                    f"< {value_node} >.",
                    nodes=argument_node.value,
                )

    if not directives or coerced_value is UNDEFINED_VALUE:
        return coerced_value
    return await directives(argument_definition, coerced_value, ctx, info)


async def coerce_arguments(
    argument_definitions: Dict[str, "GraphQLArgument"],
    node: Union["FieldNode", "DirectiveNode"],
    variable_values: Dict[str, Any],
    ctx: Optional[Any],
    info: Optional["Info"],
) -> Dict[str, Any]:
    """
    Returns the computed values of the arguments.
    :param argument_definitions: the argument definitions to treat
    :param node: the parent AST node of the arguments
    :param variable_values: the variables used in the GraphQL request
    :param ctx: context passed to the query execution
    :param info: information related to the execution and the resolved field
    :type argument_definitions: Dict[str, GraphQLArgument]
    :type node: Union[FieldNode, DirectiveNode]
    :type variable_values: Dict[str, Any]
    :type ctx: Optional[Any]
    :type info: Optional[Info]
    :return: the computed values of the arguments
    :rtype: Dict[str, Any]
    """
    # pylint: disable=too-many-locals
    argument_nodes = node.arguments
    if not argument_definitions or argument_nodes is None:
        return {}

    argument_nodes_map = {
        argument_node.name.value: argument_node
        for argument_node in argument_nodes
    }

    results = await asyncio.gather(
        *[
            argument_definition.coercer_func(
                argument_definition,
                node,
                argument_nodes_map.get(argument_definition.name),
                variable_values,
                ctx,
                info,
            )
            for argument_definition in argument_definitions.values()
        ],
        return_exceptions=True,
    )

    coercion_errors: List["GraphQLError"] = []
    coerced_values: Dict[str, Any] = {}

    for argument_name, result in zip(argument_definitions, results):
        if isinstance(result, Exception):
            coercion_errors.extend(
                located_error(
                    result, nodes=[argument_nodes_map.get(argument_name)]
                ).exceptions
            )

        # if isinstance(result, MultipleException):
        #     coercion_errors.extend(result.exceptions)
        #     continue
        #
        # if isinstance(result, Exception):
        #     coercion_errors.append(to_graphql_error(result))
        #     continue

        if result is not UNDEFINED_VALUE:
            coerced_values[argument_name] = result

    if coercion_errors:
        raise MultipleException(coercion_errors)

    return coerced_values
