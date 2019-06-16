from typing import List


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

    # TODO: implements those methods:
    # def __repr__(self) -> str:
    #     return (
    #         "{}(query_field={!r}, schema_field={!r}, schema={!r}, "
    #         "path={!r}, location={!r}, execution_ctx={!r})".format(
    #             self.__class__.__name__,
    #             self.query_field,
    #             self.schema_field,
    #             self.schema,
    #             self.path,
    #             self.location,
    #             self.execution_ctx,
    #         )
    #     )
    #
    # def __str__(self) -> str:
    #     return repr(self)
    #
    # def __eq__(self, other: Any) -> bool:
    #     return self is other or (
    #         type(self) is type(other)
    #         and (
    #             self.query_field == other.query_field
    #             and self.schema_field == other.schema_field
    #             and self.schema == other.schema
    #             and self.path == other.path
    #             and self.location == other.location
    #             and self.execution_ctx == other.execution_ctx
    #         )
    #     )


def build_resolve_info(
    execution_context: "ExecutionContext",
    field_definition: "GraphQLField",
    field_nodes: List["FieldNode"],
    parent_type: "GraphQLObjectType",
    path: "Path",
) -> "ResolveInfo":
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
