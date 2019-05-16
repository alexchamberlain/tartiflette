from typing import Any, Dict, Optional, Union

from tartiflette.language.ast import NullValueNode, VariableNode
from tartiflette.types.exceptions import GraphQLError
from tartiflette.types.helpers.definition import is_non_null_type
from tartiflette.utils.values import is_invalid_value

__all__ = ["get_argument_values"]


async def get_argument_values(
    argument_definitions: Dict[str, "GraphQLArgument"],
    node: Union["FieldNode", "DirectiveNode"],
    variable_values: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    TODO:
    :param argument_definitions: TODO:
    :param node: TODO:
    :param variable_values: TODO:
    :type argument_definitions: TODO:
    :type node: TODO:
    :type variable_values: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # pylint: disable=too-many-locals,too-many-branches
    argument_nodes = node.arguments
    if not argument_definitions or argument_nodes is None:
        return {}

    coerced_values = {}
    argument_nodes_map = {
        argument_node.name.value: argument_node
        for argument_node in argument_nodes
    }

    for argument_definition in list(argument_definitions.values()):
        name = argument_definition.name
        arg_type = argument_definition.graphql_type
        argument_node = argument_nodes_map.get(name)

        if argument_node and isinstance(argument_node.value, VariableNode):
            variable_name = argument_node.value.name.value
            has_value = variable_values and variable_name in variable_values
            is_null = has_value and variable_values[variable_name] is None
        else:
            has_value = argument_node is not None
            is_null = argument_node and isinstance(
                argument_node.value, NullValueNode
            )

        if not has_value and argument_definition.default_value is not None:
            # TODO: we should coerce `argument_definition.default_value` to
            # apply directives on it. We can't do it for now since
            # `argument_definition.default_value` is an hard coded value filled
            # in the GraphQLArgument instance and not an AST ValueNode.
            # This will be possible when the GraphQLSchema will be build
            # via a DocumentNode.
            coerced_values[name] = argument_definition.default_value
        elif (not has_value or is_null) and is_non_null_type(arg_type):
            if is_null:
                raise GraphQLError(
                    f"Argument < {name} > of non-null type < {arg_type} > "
                    "must not be null.",
                    locations=[argument_node.value.location],
                )
            if argument_node and isinstance(argument_node.value, VariableNode):
                raise GraphQLError(
                    f"Argument < {name} > of required type < {arg_type} > "
                    f"was provided the variable < ${variable_name} > which "
                    "was not provided a runtime value.",
                    locations=[argument_node.value.location],
                )
            raise GraphQLError(
                f"Argument < {name} > of required type < {arg_type} > was "
                "not provided."
            )
        elif has_value:
            if isinstance(argument_node.value, NullValueNode):
                coerced_values[name] = None
            elif isinstance(argument_node.value, VariableNode):
                variable_name = argument_node.value.name.value
                coerced_values[name] = variable_values[variable_name]
            else:
                value_node = argument_node.value
                coerced_value = await argument_definition.literal_coercer(
                    value_node, variables=variable_values
                )
                if is_invalid_value(coerced_value):
                    raise GraphQLError(
                        f"Argument < {name} > has invalid value "
                        f"< {value_node} >."
                    )
                coerced_values[name] = coerced_value
    return coerced_values
