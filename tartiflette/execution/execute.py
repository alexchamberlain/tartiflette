import asyncio

from functools import partial
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Union,
)

from tartiflette.coercers.argument import coerce_arguments
from tartiflette.coercers.common import Path
from tartiflette.constants import UNDEFINED_VALUE
from tartiflette.execution.collect import collect_executables
from tartiflette.language.ast import (
    FieldNode,
    FragmentSpreadNode,
    InlineFragmentNode,
)
from tartiflette.types.exceptions.tartiflette import SkipCollection
from tartiflette.types.helpers import transform_directive
from tartiflette.types.helpers.definition import (
    get_wrapped_type,
    is_abstract_type,
    is_leaf_type,
    is_list_type,
    is_non_null_type,
    is_object_type,
)
from tartiflette.types.helpers.wraps_with_directives import (
    wraps_with_directives,
)
from tartiflette.utils.coercer_way import CoercerWay
from tartiflette.utils.errors import graphql_error_from_nodes, located_error
from tartiflette.utils.type_from_ast import schema_type_from_ast
from tartiflette.utils.values import is_invalid_value

# pylint: disable=too-many-lines


class ResolveInfo:
    """
    TODO:
    """

    __slots__ = (
        "field_name",
        "field_nodes",
        "return_type",
        "parent_type",
        "path",
        "schema",
        "fragments",
        "root_value",
        "operation",
        "variable_values",
    )

    def __init__(
        self,
        field_name,
        field_nodes,
        return_type,
        parent_type,
        path,
        schema,
        fragments,
        root_value,
        operation,
        variable_values,
    ):
        """
        TODO:
        :param field_name: TODO:
        :param field_nodes: TODO:
        :param return_type: TODO:
        :param parent_type: TODO:
        :param path: TODO:
        :param schema: TODO:
        :param fragments: TODO:
        :param root_value: TODO:
        :param operation: TODO:
        :param variable_values: TODO:
        :type field_name: TODO:
        :type field_nodes: TODO:
        :type return_type: TODO:
        :type parent_type: TODO:
        :type path: TODO:
        :type schema: TODO:
        :type fragments: TODO:
        :type root_value: TODO:
        :type operation: TODO:
        :type variable_values: TODO:
        """
        # pylint: disable=too-many-arguments,too-many-locals
        self.field_name = field_name
        self.field_nodes = field_nodes
        self.return_type = return_type
        self.parent_type = parent_type
        self.path = path
        self.schema = schema
        self.fragments = fragments
        self.root_value = root_value
        self.operation = operation
        self.variable_values = variable_values


async def should_include_node(
    execution_context: "ExecutionContext",
    node: Union["FragmentSpreadNode", "FieldNode", "InlineFragmentNode"],
) -> bool:
    """
    Determines if a field should be included based on the @include and @skip
    directives, where @skip has higher precedence than @include.
    :param execution_context: TODO:
    :param node: TODO:
    :type execution_context: TODO:
    :type node: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # TODO: refactor this a improve it
    if not node.directives:
        return True

    computed_directives = []
    for directive_node in node.directives:
        try:
            directive_definition = execution_context.schema.find_directive(
                directive_node.name.value
            )
            computed_directives.append(
                transform_directive(
                    directive_definition,
                    args=partial(
                        coerce_arguments,
                        argument_definitions=directive_definition.arguments,
                        node=directive_node,
                        variable_values=execution_context.variable_values,
                        ctx=execution_context.context,
                        info=None,  # TODO: expected a "ResolveInfo" instance but we don't have it
                    ),
                )
            )
        except Exception as e:  # pylint: disable=broad-except,unused-variable
            # TODO: we should add the error to the context here
            return False

    hook_name = (
        "on_field_collection"
        if isinstance(node, FieldNode)
        else (
            "on_fragment_spread_collection"
            if isinstance(node, FragmentSpreadNode)
            else "on_inline_fragment_collection"
        )
    )

    try:
        await wraps_with_directives(computed_directives, hook_name)(node)
    except SkipCollection:
        return False
    except Exception as e:  # pylint: disable=broad-except,unused-variable
        # TODO: we should add the error to the context here
        return False
    return True


def get_field_entry_key(node: "FieldNode") -> str:
    """
    Implements the logic to compute the key of a given field's entry.
    :param node: TODO:
    :type node: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return node.alias.value if node.alias else node.name.value


def does_fragment_condition_match(
    execution_context: "ExecutionContext",
    fragment_node: Union["FragmentDefinitionNode", "InlineFragmentNode"],
    graphql_object_type: "GraphQLObjectType",
) -> bool:
    """
    Determines if a fragment is applicable to the given type.
    :param execution_context: TODO:
    :param fragment_node: TODO:
    :param graphql_object_type: TODO:
    :type execution_context: TODO:
    :type fragment_node: TODO:
    :type graphql_object_type: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    type_condition_node = fragment_node.type_condition
    if not type_condition_node:
        return True

    conditional_type = schema_type_from_ast(
        execution_context.schema, type_condition_node
    )
    if conditional_type is graphql_object_type:  # TODO: is or == ?
        return True

    return is_abstract_type(
        conditional_type
    ) and conditional_type.is_possible_type(graphql_object_type)


async def collect_fields(
    execution_context: "ExecutionContext",
    runtime_type: "GraphQLObjectType",
    selection_set: "SelectionSetNode",
    fields: Optional[Dict[str, List["FieldNode"]]] = None,
    visited_fragment_names: Optional[Set[str]] = None,
) -> Dict[str, List["FieldNode"]]:
    """
    Given a selectionSet, adds all of the fields in that selection to
    the passed in map of fields, and returns it at the end.

    CollectFields requires the "runtime type" of an object. For a field which
    returns an Interface or Union type, the "runtime type" will be the actual
    Object type returned by that field.
    :param execution_context: TODO:
    :param runtime_type: TODO:
    :param selection_set: TODO:
    :param fields: TODO:
    :param visited_fragment_names: TODO:
    :type execution_context: TODO:
    :type runtime_type: TODO:
    :type selection_set: TODO:
    :type fields: TODO:
    :type visited_fragment_names: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    if fields is None:
        fields: Dict[str, "FieldNode"] = {}

    if visited_fragment_names is None:
        visited_fragment_names: Set[str] = set()

    for selection in selection_set.selections:
        if isinstance(selection, FieldNode):
            if not await should_include_node(execution_context, selection):
                continue
            fields.setdefault(get_field_entry_key(selection), []).append(
                selection
            )
        elif isinstance(selection, InlineFragmentNode):
            if not await should_include_node(
                execution_context, selection
            ) or not does_fragment_condition_match(
                execution_context, selection, runtime_type
            ):
                continue

            await collect_fields(
                execution_context,
                runtime_type,
                selection.selection_set,
                fields,
                visited_fragment_names,
            )
        elif isinstance(selection, FragmentSpreadNode):
            fragment_name = selection.name.value
            if (
                fragment_name in visited_fragment_names
                or not await should_include_node(execution_context, selection)
            ):
                continue

            visited_fragment_names.add(fragment_name)

            fragment_definition = execution_context.fragments[fragment_name]
            if not fragment_definition or not does_fragment_condition_match(
                execution_context, fragment_definition, runtime_type
            ):
                continue

            await collect_fields(
                execution_context,
                runtime_type,
                fragment_definition.selection_set,
                fields,
                visited_fragment_names,
            )
    return fields


async def execute_fields_serially(
    execution_context: "ExecutionContext",
    parent_type: "GraphQLObjectType",
    source_value: Any,
    path: Optional["ResponsePath"],
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
        if (
            result is not UNDEFINED_VALUE
        ):  # TODO: not sure that can be the case
            results[entry_key] = result
    return results


async def execute_fields(
    execution_context: "ExecutionContext",
    parent_type: "GraphQLObjectType",
    source_value: Any,
    path: Optional["ResponsePath"],
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
        if result is not UNDEFINED_VALUE  # TODO: not sure that could happened
    }


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


async def execute_operation_n(
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


def build_resolve_info(
    execution_context: "ExecutionContext",
    field_definition: "GraphQLField",
    field_nodes: List["FieldNode"],
    parent_type: "GraphQLObjectType",
    path: "ResponsePath",
) -> "GraphQLResolveInfo":
    """
    TODO:
    :param execution_context: TODO:
    :param field_definition: TODO:
    :param field_nodes: TODO:
    :param parent_type: TODO:
    :param path: TODO:
    :type execution_context: TODO:
    :type field_definition: TODO:
    :type field_nodes: TODO:
    :type parent_type: TODO:
    :type path: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return ResolveInfo(
        field_definition.name,
        field_nodes,
        field_definition.graphql_type,  # TODO: is it the correct attribute?
        parent_type,
        path,
        execution_context.schema,
        execution_context.fragments,
        execution_context.root_value,
        execution_context.operation,
        execution_context.variable_values,
    )


async def resolve_field_value_or_error(
    execution_context: "ExecutionContext",
    field_definition: "GraphQLField",
    field_nodes: List["FieldNode"],
    resolver: Callable,
    source: Any,
    info: "GraphQLResolveInfo",
) -> Union[Exception, Any]:
    """
    Isolates the "ReturnOrAbrupt" behavior to not de-opt the `resolveField`
    function. Returns the result of resolveFn or the abrupt-return Error
    object.
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
    # pylint: disable=too-many-locals
    try:
        resolver = wraps_with_directives(
            directives_definition=field_definition.directives,
            directive_hook="on_field_execution",
            func=resolver,
        )

        computed_directives = []
        for field_node in field_nodes:
            for directive_node in field_node.directives:
                try:
                    directive_definition = execution_context.schema.find_directive(
                        directive_node.name.value
                    )
                    computed_directives.append(
                        transform_directive(
                            directive_definition,
                            args=partial(
                                coerce_arguments,
                                argument_definitions=directive_definition.arguments,
                                node=directive_node,
                                variable_values=execution_context.variable_values,
                                ctx=execution_context.context,
                                info=None,
                                # TODO: expected a "ResolveInfo" instance but we don't have it
                            ),
                        )
                    )
                except Exception as e:  # pylint: disable=broad-except,unused-variable
                    # TODO: we should add the error to the context here
                    pass

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


async def complete_list_value(
    execution_context: "ExecutionContext",
    return_type: "GraphQLOuputType",
    field_nodes: List["FieldNode"],
    info: "GraphQLResolveInfo",
    path: "ResponsePath",
    result: Any,
) -> Any:
    """
    Complete a list value by completing each item in the list with the
    inner type.
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
    if not isinstance(result, list):
        raise TypeError(
            "Expected Iterable, but did not find one for field "
            f"{info.parent_type.name}.{info.field_name}."
        )

    item_type = return_type.wrapped_type

    return [
        await complete_value_catching_error(
            execution_context,
            item_type,
            field_nodes,
            info,
            Path(path, index),
            item,
        )
        for index, item in enumerate(result)
    ]


async def complete_leaf_value(
    return_type: "GraphQLOuputType", result: Any
) -> Any:
    """
    Complete a Scalar or Enum by serializing to a valid value, returning
    null if serialization is not possible.
    :param return_type: TODO:
    :param result: TODO:
    :type return_type: TODO:
    :type result: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    serialized_result = return_type.coerce_output(result)
    if is_invalid_value(serialized_result):
        raise ValueError(
            f"Expected value of type {return_type} but received {type(result)}."
        )
    return serialized_result


def ensure_valid_runtime_type(
    runtime_type_or_name: Union["GraphQLObjectType", str],
    execution_context: "ExecutionContext",
    return_type: "GraphQLAbstractType",
    field_nodes: List["FieldNodes"],
    info: "GraphQLResolveInfo",
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


async def complete_abstract_value(
    execution_context: "ExecutionContext",
    return_type: "GraphQLOuputType",
    field_nodes: List["FieldNode"],
    info: "GraphQLResolveInfo",
    path: "ResponsePath",
    result: Any,
):
    """
    Complete a value of an abstract type by determining the runtime object type
    of that value, then complete the value for that type.
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
    type_resolver = (
        return_type.type_resolver
        if hasattr(return_type, "type_resolver") and return_type.type_resolver
        else execution_context.default_type_resolver
    )

    return await complete_object_value(
        execution_context,
        ensure_valid_runtime_type(
            await type_resolver(
                result, execution_context.context, info, return_type
            ),
            execution_context,
            return_type,
            field_nodes,
            info,
            result,
        ),
        field_nodes,
        info,
        path,
        result,
    )


async def collect_subfields(
    execution_context: "ExecutionContext",
    return_type: "GraphQLOuputType",
    field_nodes: List["FieldNode"],
) -> Dict[str, List["FieldNode"]]:
    """
    A memoized collection of relevant subfields with regard to the return
    type. Memoizing ensures the subfields are not repeatedly calculated, which
    saves overhead when resolving lists of values.
    :param execution_context: TODO:
    :param return_type: TODO:
    :param field_nodes: TODO:
    :type execution_context: TODO:
    :type return_type: TODO:
    :type field_nodes: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    subfield_nodes: Dict[str, List["FieldNode"]] = {}
    visited_fragment_names: Set[str] = set()
    for field_node in field_nodes:
        selection_set = field_node.selection_set
        if selection_set:
            subfield_nodes = await collect_fields(
                execution_context,
                return_type,
                selection_set,
                subfield_nodes,
                visited_fragment_names,
            )
    return subfield_nodes


async def collect_and_execute_subfields(
    execution_context: "ExecutionContext",
    return_type: "GraphQLOuputType",
    field_nodes: List["FieldNode"],
    path: "ResponsePath",
    result: Any,
) -> Dict[str, Any]:
    """
    TODO:
    :param execution_context: TODO:
    :param return_type: TODO:
    :param field_nodes: TODO:
    :param path: TODO:
    :param result: TODO:
    :type execution_context: TODO:
    :type return_type: TODO:
    :type field_nodes: TODO:
    :type path: TODO:
    :type result: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return await execute_fields(
        execution_context,
        return_type,
        result,
        path,
        await collect_subfields(execution_context, return_type, field_nodes),
    )


async def complete_object_value(
    execution_context: "ExecutionContext",
    return_type: "GraphQLOuputType",
    field_nodes: List["FieldNode"],
    info: "GraphQLResolveInfo",
    path: "ResponsePath",
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
    return await collect_and_execute_subfields(
        execution_context, return_type, field_nodes, path, result
    )


async def complete_value(
    execution_context: "ExecutionContext",
    return_type: "GraphQLOutputType",
    field_nodes: List["FieldNode"],
    info: "GraphQLResolveInfo",
    path: "ResponsePath",
    result: Any,
) -> Any:
    """
    Implements the instructions for completeValue as defined in the
    "Field entries" section of the spec.

    If the field type is Non-Null, then this recursively completes the value
    for the inner type. It throws a field error if that completion returns null,
    as per the "Nullability" section of the spec.

    If the field type is a List, then this recursively completes the value
    for the inner type on each item in the list.

    If the field type is a Scalar or Enum, ensures the completed value is a legal
    value of the type by calling the `serialize` method of GraphQL type
    definition.

    If the field is an abstract type, determine the runtime type of the value
    and then complete based on that type

    Otherwise, the field type expects a sub-selection set, and will complete the
    value by evaluating all sub-selections.
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
    if isinstance(result, Exception):
        raise result

    if is_non_null_type(return_type):
        completed = await complete_value(
            execution_context,
            return_type.wrapped_type,
            field_nodes,
            info,
            path,
            result,
        )
        if completed is None:
            raise ValueError(
                "Cannot return null for non-nullable field "
                f"{info.parent_type.name}.{info.field_name}."
            )
        return completed

    if result is None:
        return None

    if is_list_type(return_type):
        return await complete_list_value(
            execution_context, return_type, field_nodes, info, path, result
        )

    if is_leaf_type(return_type):
        return await complete_leaf_value(return_type, result)

    if is_abstract_type(return_type):
        return await complete_abstract_value(
            execution_context, return_type, field_nodes, info, path, result
        )

    if is_object_type(return_type):
        return await complete_object_value(
            execution_context, return_type, field_nodes, info, path, result
        )

    raise TypeError(
        f"Cannot complete value of unexpected output type: {return_type}."
    )


def handle_field_error(
    raw_error: Exception,
    field_nodes: List["FieldNode"],
    path: "ResponsePath",
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
    return_type: "GraphQLOutputType",
    field_nodes: List["FieldNode"],
    info: "GraphQLResolveInfo",
    path: "ResponsePath",
    result: Any,
) -> Any:
    """
    This is a small wrapper around completeValue which detects and logs errors.
    in the execution context.
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
    try:
        return await complete_value(
            execution_context, return_type, field_nodes, info, path, result
        )
    except Exception as raw_exception:  # pylint: disable=broad-except
        return handle_field_error(
            raw_exception, field_nodes, path, return_type, execution_context
        )


async def resolve_field(
    execution_context: "ExecutionContext",
    parent_type: "GraphQLObjectType",
    source: Any,
    field_nodes: List["FieldNode"],
    path: "ResponsePath",
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

    info = build_resolve_info(
        execution_context, field_definition, field_nodes, parent_type, path
    )

    result = await resolve_field_value_or_error(
        execution_context,
        field_definition,
        field_nodes,
        field_definition.raw_resolver
        or execution_context.default_field_resolver,
        source,
        info,
    )

    return await complete_value_catching_error(
        execution_context,
        field_definition.graphql_type,  # TODO: is it the correct attribute?
        field_nodes,
        info,
        path,
        result,
    )


###########
# OLD NEW #
###########
def _get_executable_fields_data(
    operation_executable_fields: List["ExecutableFieldNode"]
) -> Optional[Dict[str, Any]]:
    data = {}
    for field in operation_executable_fields:
        if field.cant_be_null and field.marshalled is None:
            return None
        if not field.is_execution_stopped:
            data[field.alias] = field.marshalled

    return data or None


async def _execute_fields_serially(
    fields: List["ExecutableFieldNode"],
    execution_context: "ExecutionContext",
    initial_value: Optional[Any],
) -> None:
    for field in fields:
        await field(
            execution_context,
            execution_context.context,
            parent_result=initial_value,
        )


async def _execute_fields(
    fields: List["ExecutableFieldNode"],
    execution_context: "ExecutionContext",
    initial_value: Optional[Any],
) -> None:
    await asyncio.gather(
        *[
            field(
                execution_context,
                execution_context.context,
                parent_result=initial_value,
            )
            for field in fields
        ],
        return_exceptions=False,
    )


async def execute_operation(
    execution_context: "ExecutionContext"
) -> Dict[str, Any]:
    operation_type = execution_context.schema.find_type(
        execution_context.schema.get_operation_type(
            execution_context.operation.operation_type.capitalize()
        )
    )

    operation_executable_map_fields = await collect_executables(
        execution_context,
        operation_type,
        execution_context.operation.selection_set,
    )

    if execution_context.errors:
        return execution_context.build_response(
            errors=execution_context.errors
        )

    if not operation_executable_map_fields:
        return execution_context.build_response()

    operation_executable_fields = list(
        operation_executable_map_fields[operation_type.name].values()
    )

    if execution_context.operation.operation_type == "mutation":
        await _execute_fields_serially(
            operation_executable_fields,
            execution_context,
            execution_context.root_value,
        )
    else:
        await _execute_fields(
            operation_executable_fields,
            execution_context,
            execution_context.root_value,
        )

    return execution_context.build_response(
        data=_get_executable_fields_data(operation_executable_fields),
        errors=execution_context.errors,
    )


async def run_subscription(
    execution_context: "ExecutionContext"
) -> AsyncIterable[Dict[str, Any]]:
    operation_type = execution_context.schema.find_type(
        execution_context.schema.get_operation_type(
            execution_context.operation.operation_type.capitalize()
        )
    )

    operation_executable_map_fields = await collect_executables(
        execution_context,
        operation_type,
        execution_context.operation.selection_set,
    )

    if execution_context.errors:
        yield execution_context.build_response(errors=execution_context.errors)
        return

    if not operation_executable_map_fields:
        yield execution_context.build_response()
        return

    operation_executable_fields = list(
        operation_executable_map_fields[operation_type.name].values()
    )

    source_event_stream = await operation_executable_fields[
        0
    ].create_source_event_stream(
        execution_context, execution_context.root_value
    )

    async for message in source_event_stream:
        await _execute_fields(
            operation_executable_fields, execution_context, message
        )
        yield execution_context.build_response(
            data=_get_executable_fields_data(operation_executable_fields),
            errors=execution_context.errors,
        )
