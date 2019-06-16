import asyncio

from typing import Any, Dict, List, Optional

from tartiflette.coercers.common import Path
from tartiflette.constants import UNDEFINED_VALUE
from tartiflette.execution.collect import collect_fields
from tartiflette.language.ast import FieldNode
from tartiflette.utils.errors import graphql_error_from_nodes


def get_field_definition(
    schema: "GraphQLSchema", parent_type: "GraphQLObjectType", field_name: str
) -> "GraphQLField":
    """
    This method looks up the field on the given type definition.
    It has special casing for the two introspection fields, __schema
    and __typename. __typename is special because it can always be
    queried as a field, even in situations where no other fields
    are allowed, like on a Union. __schema could get automatically
    added to the query type, but that would require mutating type
    definitions, which would cause issues.
    :param schema: TODO:
    :param parent_type: TODO:
    :param field_name: TODO:
    :type schema: TODO:
    :type parent_type: TODO:
    :type field_name: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    try:
        parent_field = schema.get_field_by_name(f"{parent_type}.{field_name}")
        if parent_field is not None:
            return parent_field
    except Exception:  # pylint: disable=broad-except
        pass
    return None

    # TODO: implements this please!
    # if field_name == SchemaMetaFieldDefinition.name and parent_type is schema.query_type:
    #     return SchemaMetaFieldDefinition
    # if field_name == TypeMetaFieldDef.name and parent_type is schema.query_type:
    #     return TypeMetaFieldDef
    # if field_name == TypeNameMetaFieldDef.name:
    #     return TypeNameMetaFieldDef


async def resolve_field(
    execution_context: "ExecutionContext",
    parent_type: "GraphQLObjectType",
    source: Any,
    field_nodes: List["FieldNode"],
    path: "Path",
) -> Any:
    """
    Resolves the field on the given source object. In particular, this
    figures out the value that the field returns by calling its resolve
    function, then calls completeValue to complete promises, serialize scalars,
    or execute the sub-selection-set for objects.
    :param execution_context: TODO:
    :param parent_type: TODO:
    :param source: TODO:
    :param field_nodes: TODO:
    :param path: TODO:
    :type execution_context: TODO:
    :type parent_type: TODO:
    :type source: TODO:
    :type field_nodes: TODO:
    :type path: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    field_node = field_nodes[0]
    field_name = field_node.name.value

    field_definition = get_field_definition(
        execution_context.schema, parent_type, field_name
    )
    if field_definition is None:  # TODO: should never happened, isn't?
        return UNDEFINED_VALUE

    return await field_definition.resolver(
        execution_context, parent_type, source, field_nodes, path
    )


def get_operation_root_type(
    schema: "GraphQLSchema", operation: "OperationDefinitionNode"
) -> "GraphQLObjectType":
    """
    Extracts the root type of the operation from the schema.
    :param schema: TODO:
    :param operation: TODO:
    :type schema: TODO:
    :type operation: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    operation_type = operation.operation_type
    if operation_type == "query":
        try:
            return schema.find_type(schema.query_type)
        except KeyError:
            raise graphql_error_from_nodes(
                "Schema does not define the required query root type.",
                nodes=operation,
            )
    if operation_type == "mutation":
        try:
            return schema.find_type(schema.mutation_type)
        except KeyError:
            raise graphql_error_from_nodes(
                "Schema is not configured for mutations.", nodes=operation
            )
    if operation_type == "subscription":
        try:
            return schema.find_type(schema.subscription_type)
        except KeyError:
            raise graphql_error_from_nodes(
                "Schema is not configured for subscriptions.", nodes=operation
            )
    raise graphql_error_from_nodes(
        "Can only have query, mutation and subscription operations.",
        nodes=operation,
    )


async def execute_fields_serially(
    execution_context: "ExecutionContext",
    parent_type: "GraphQLObjectType",
    source_value: Any,
    path: Optional["Path"],
    fields: Dict[str, List["FieldNode"]],
) -> Dict[str, Any]:
    """
    Implements the "Evaluating selection sets" section of the spec for "write"
    mode.
    :param execution_context: TODO:
    :param parent_type: TODO:
    :param source_value: TODO:
    :param path: TODO:
    :param fields: TODO:
    :type execution_context: TODO:
    :type parent_type: TODO:
    :type source_value: TODO:
    :type path: TODO:
    :type fields: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    results = {}
    for entry_key, field_nodes in fields.items():
        result = await resolve_field(
            execution_context,
            parent_type,
            source_value,
            field_nodes,
            Path(path, entry_key),
        )
        if result is not UNDEFINED_VALUE:
            results[entry_key] = result
    return results


async def execute_fields(
    execution_context: "ExecutionContext",
    parent_type: "GraphQLObjectType",
    source_value: Any,
    path: Optional["Path"],
    fields: Dict[str, List["FieldNode"]],
) -> Dict[str, Any]:
    """
    Implements the "Evaluating selection sets" section of the spec for "read"
    mode.
    :param execution_context: TODO:
    :param parent_type: TODO:
    :param source_value: TODO:
    :param path: TODO:
    :param fields: TODO:
    :type execution_context: TODO:
    :type parent_type: TODO:
    :type source_value: TODO:
    :type path: TODO:
    :type fields: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    results = await asyncio.gather(
        *[
            resolve_field(
                execution_context,
                parent_type,
                source_value,
                field_nodes,
                Path(path, entry_key),
            )
            for entry_key, field_nodes in fields.items()
        ]
    )

    return {
        entry_key: result
        for entry_key, result in zip(fields, results)
        if result is not UNDEFINED_VALUE
    }


async def execute_operation(
    execution_context: "ExecutionContext",
    operation: "OperationDefinitionNode",
    root_value: Optional[Any],
) -> Optional[Dict[str, Any]]:
    """
    Implements the "Evaluating operations" section of the spec.
    :param execution_context: TODO:
    :param operation: TODO:
    :param root_value: TODO:
    :type execution_context: TODO:
    :type operation: TODO:
    :type root_value: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    operation_root_type = get_operation_root_type(
        execution_context.schema, operation
    )

    fields = await collect_fields(
        execution_context, operation_root_type, operation.selection_set
    )

    try:
        return await (
            execute_fields_serially(
                execution_context,
                operation_root_type,
                root_value,
                None,
                fields,
            )
            if operation.operation_type == "mutation"
            else execute_fields(
                execution_context,
                operation_root_type,
                root_value,
                None,
                fields,
            )
        )
    except Exception as e:  # pylint: disable=broad-except
        execution_context.add_error(e)  # TODO: should we add location?
        return None
