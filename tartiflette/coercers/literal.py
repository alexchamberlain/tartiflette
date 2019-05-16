from functools import partial
from typing import Any, Callable, Dict, Optional, Union

from tartiflette.constants import UNDEFINED_VALUE
from tartiflette.language.ast import (
    EnumValueNode,
    ListValueNode,
    NullValueNode,
    ObjectValueNode,
    VariableNode,
)
from tartiflette.types.helpers import wraps_with_directives
from tartiflette.types.helpers.definition import (
    get_wrapped_type,
    is_enum_type,
    is_input_object_type,
    is_list_type,
    is_non_null_type,
    is_scalar_type,
    is_wrapping_type,
)
from tartiflette.utils.coercer_way import CoercerWay
from tartiflette.utils.values import is_invalid_value


def is_missing_variable(
    value_node: Union["ValueNode", "VariableNode"], variables: Dict[str, Any]
) -> bool:
    """
    Determines whether or not the value node is a VariableNode without defined
    value.
    :param value_node: the AST node to treat
    :param variables: the variables used in the GraphQL request
    :type value_node: Union[ValueNode, VariableNode]
    :type variables: Dict[str, Any]
    :return: whether or not the value node is a VariableNode without defined
    value
    :rtype: bool
    """
    return isinstance(value_node, VariableNode) and (
        not variables
        or value_node.name.value not in variables
        or is_invalid_value(variables[value_node.name.value])
    )


def null_and_variable_coercer_wrapper(coercer: Callable) -> Any:
    """
    Factorization of the treatment making it possible to coerce a NullValueNode
    or a VariableNode.
    :param coercer: the pre-computed coercer to use on the value if not a
    NullValueNode neither a VariableNode
    :type coercer: Callable
    :return: the computed value
    :rtype: Any
    """

    async def wrapper(node, *args, variables=None, **kwargs):
        if not node:
            return UNDEFINED_VALUE

        if isinstance(node, NullValueNode):
            return None

        if isinstance(node, VariableNode):
            if not variables:
                return UNDEFINED_VALUE

            value = variables.get(node.name.value, UNDEFINED_VALUE)
            if is_invalid_value(value):
                return UNDEFINED_VALUE

            # TODO: check this
            # if value is None and is_non_null_type(schema_type):
            #     return UNDEFINED_VALUE
            return value

        return await coercer(node, *args, variables=variables, **kwargs)

    return wrapper


@null_and_variable_coercer_wrapper
async def scalar_coercer(
    node: Union["ValueNode", "VariableNode"],
    scalar: "GraphQLScalarType",
    variables: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Computes the value of a scalar.
    :param node: the AST node to treat
    :param scalar: the GraphQLScalarType instance of the scalar
    :param variables: the variables used in the GraphQL request
    :type node: Union[ValueNode, VariableNode]
    :type scalar: GraphQLScalarType
    :type variables: Optional[Dict[str, Any]]
    :return: the computed value
    :rtype: Any
    """
    # pylint: disable=unused-argument
    try:
        value = scalar.parse_literal(node)
        if not is_invalid_value(value):
            return value
    except Exception:  # pylint: disable=broad-except
        pass
    return UNDEFINED_VALUE


@null_and_variable_coercer_wrapper
async def enum_coercer(
    node: Union["ValueNode", "VariableNode"],
    enum: "GraphQLEnumType",
    variables: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Computes the value of an enum.
    :param node: the AST node to treat
    :param enum: the GraphQLEnumType instance of the enum
    :param variables: the variables used in the GraphQL request
    :type node: Union[ValueNode, VariableNode]
    :type enum: GraphQLEnumType
    :type variables: Optional[Dict[str, Any]]
    :return: the computed value
    :rtype: Any
    """
    # pylint: disable=unused-argument
    if not isinstance(node, EnumValueNode):
        return UNDEFINED_VALUE

    try:
        enum_value = enum.get_enum_value(node.value)

        # TODO: Wait, That's Illegal
        faker = {"ctx": None, "argument_definition": None, "info": None}

        return await enum_value.directives[
            CoercerWay.INPUT
        ](  # TODO: do better
            node.value, **faker
        )
    except KeyError:
        return UNDEFINED_VALUE


@null_and_variable_coercer_wrapper
async def input_object_coercer(
    node: Union["ValueNode", "VariableNode"],
    input_object: "GraphQLInputObjectType",
    input_field_coercers: Dict[str, Callable],
    variables: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Computes the value of an input object.
    :param node: the AST node to treat
    :param input_object: the GraphQLInputObjectType instance of the input
    object
    :param input_field_coercers: a dictionary of pre-computed coercer for each
    input fields
    :param variables: the variables used in the GraphQL request
    :type node: Union[ValueNode, VariableNode]
    :type input_object: GraphQLInputObjectType
    :type input_field_coercers: Dict[str, Callable]
    :type variables: Optional[Dict[str, Any]]
    :return: the computed value
    :rtype: Any
    """
    if not isinstance(node, ObjectValueNode):
        return UNDEFINED_VALUE

    field_nodes = {
        field_node.name.value: field_node for field_node in node.fields
    }
    fields = input_object.arguments

    coerced_object = {}
    for field_name, field in fields.items():
        if field_name not in field_nodes or is_missing_variable(
            field_nodes[field_name].value, variables
        ):
            # TODO: at schema build we should use UNDEFINED_VALUE for
            # `default_value` attribute of a field to know if a field has
            # a defined default value (since default value could be `None`)
            # once done, we should check for `UNDEFINED_VALUE` here.
            if field.default_value is not None:
                # TODO: we should coerce `field.default_value` to apply
                # directives on it. We can't do it for now since
                # `field.default_value` is an hard coded value filled in the
                # GraphQLArgument instance and not an AST ValueNode.
                # This will be possible when the GraphQLSchema will be build
                # via a DocumentNode.
                coerced_object[field_name] = field.default_value
            elif is_non_null_type(field.graphql_type):
                return UNDEFINED_VALUE
            continue

        field_value = await input_field_coercers[field_name](
            field_nodes[field_name].value, variables=variables
        )
        if is_invalid_value(field_value):
            return UNDEFINED_VALUE
        coerced_object[field_name] = field_value
    return coerced_object


@null_and_variable_coercer_wrapper
async def list_coercer(
    node: Union["ValueNode", "VariableNode"],
    is_non_null_item_type: bool,
    inner_coercer: Callable,
    variables: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Computes the value of a list.
    :param node: the AST node to treat
    :param is_non_null_item_type: determines whether or not the inner value is
    nullable
    :param inner_coercer: the pre-computed coercer to use on each value in the
    list
    :param variables: the variables used in the GraphQL request
    :type node: Union[ValueNode, VariableNode]
    :type is_non_null_item_type: bool
    :type inner_coercer: Callable
    :type variables: Optional[Dict[str, Any]]
    :return: the computed value
    :rtype: Any
    """
    if isinstance(node, ListValueNode):
        coerced_values = []
        for item_node in node.values:
            if is_missing_variable(item_node, variables):
                if is_non_null_item_type:
                    return UNDEFINED_VALUE
                coerced_values.append(None)
                continue

            item_value = await inner_coercer(item_node, variables=variables)
            if is_invalid_value(item_value):
                return UNDEFINED_VALUE
            coerced_values.append(item_value)
        return coerced_values

    coerced_value = await inner_coercer(node, variables=variables)
    if is_invalid_value(coerced_value):
        return UNDEFINED_VALUE
    return [coerced_value]


async def non_null_coercer(
    node: Union["ValueNode", "VariableNode"],
    inner_coercer: Callable,
    variables: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Checks if the value is NullValueNode and will raise an error if its the
    case or will try to coerce it.
    :param node: the AST node to treat
    :param inner_coercer: the pre-computed coercer to use on the value
    :param variables: the variables used in the GraphQL request
    :type node: Union[ValueNode, VariableNode]
    :type inner_coercer: Callable
    :type variables: Optional[Dict[str, Any]]
    :return: the computed value
    :rtype: Any
    """
    if isinstance(node, NullValueNode):
        return UNDEFINED_VALUE

    return await inner_coercer(node, variables=variables)


async def literal_directives_coercer(
    node: Union["ValueNode", "VariableNode"],
    coercer: Callable,
    directives: Callable,
    variables: Optional[Dict[str, Any]] = None,
    is_input_field: bool = False,
) -> Any:
    """
    Executes the directives on the coerced value.
    :param node: the AST node to treat
    :param coercer: pre-computed coercer to use on the value
    :param directives: the directives to execute
    :param variables: the variables used in the GraphQL request
    :param is_input_field: determines whether or not the node is an InputField
    :type node: Union[ValueNode, VariableNode]
    :type coercer: Callable
    :type directives: Callable
    :type variables: Optional[Dict[str, Any]]
    :type is_input_field: bool
    :return: the computed value
    :rtype: Any
    """
    result = await coercer(node, variables=variables)

    if (
        not directives
        or result is UNDEFINED_VALUE
        or (isinstance(node, VariableNode) and not is_input_field)
    ):
        return result

    # TODO: Wait, That's Illegal
    faker = {"ctx": None, "argument_definition": None, "info": None}

    return await directives(result, **faker)


def get_literal_coercer(schema_type: "GraphQLType") -> Callable:
    """
    Computes and returns the coercer to use for the filled in schema type.
    :param schema_type: the schema type for which compute the coercer
    :type schema_type: GraphQLType
    :return: the computed coercer wrap with directives if defined
    :rtype: Callable
    """
    wrapped_type = get_wrapped_type(schema_type)

    wrapped_type_directives = (
        getattr(wrapped_type, "directives_definition", None) or []
    )

    if is_scalar_type(wrapped_type):
        coercer = partial(scalar_coercer, scalar=wrapped_type)
    elif is_enum_type(wrapped_type):
        coercer = partial(enum_coercer, enum=wrapped_type)
    elif is_input_object_type(wrapped_type):
        coercer = partial(
            input_object_coercer,
            input_object=wrapped_type,
            input_field_coercers={
                name: partial(
                    literal_directives_coercer,
                    coercer=get_literal_coercer(argument.graphql_type),
                    directives=wraps_with_directives(
                        directives_definition=getattr(
                            argument, "directives_definition", None
                        )
                        or [],
                        directive_hook="on_post_input_coercion",
                    ),
                    is_input_field=True,
                )
                for name, argument in wrapped_type.arguments.items()
            },
        )
    else:
        coercer = lambda *args, **kwargs: None  # Not an InputType anyway...

    if wrapped_type_directives:
        directives = wraps_with_directives(
            directives_definition=wrapped_type_directives,
            directive_hook="on_post_input_coercion",
        )
        if directives:
            coercer = partial(
                literal_directives_coercer,
                coercer=coercer,
                directives=directives,
            )

    inner_type = schema_type
    wrapper_coercers = []
    while is_wrapping_type(inner_type):
        wrapped_type = inner_type.wrapped_type
        if is_list_type(inner_type):
            wrapper_coercers.append(
                partial(
                    list_coercer,
                    is_non_null_item_type=is_non_null_type(wrapped_type),
                )
            )
        elif is_non_null_type(inner_type):
            wrapper_coercers.append(non_null_coercer)
        inner_type = wrapped_type

    for wrapper_coercer in reversed(wrapper_coercers):
        coercer = partial(wrapper_coercer, inner_coercer=coercer)

    return coercer
