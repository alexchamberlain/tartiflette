from functools import lru_cache
from typing import List, Optional, Tuple, Union

from tartiflette.execution.nodes.variable_definition import (
    variable_definition_node_to_executable,
)
from tartiflette.language.parsers.libgraphqlparser import parse_to_document
from tartiflette.types.exceptions import GraphQLError
from tartiflette.utils.errors import to_graphql_error

__all__ = (
    "parse_and_validate_query",
    "collect_executable_variable_definitions",
)


@lru_cache(maxsize=1024)
def parse_and_validate_query(
    query: Union[str, bytes]
) -> Tuple[Optional["DocumentNode"], Optional[List["GraphQLError"]]]:
    """
    Analyzes & validates a query by converting it to a DocumentNode.
    :param query: the GraphQL request / query as UTF8-encoded string
    :type query: Union[str, bytes]
    :return: a DocumentNode representing the query
    :rtype: Tuple[Optional[DocumentNode], Optional[List[GraphQLError]]]
    """
    try:
        document: "DocumentNode" = parse_to_document(query)
    except GraphQLError as e:
        return None, [e]
    except Exception as e:  # pylint: disable=broad-except
        return (
            None,
            [to_graphql_error(e, message="Server encountered an error.")],
        )
    # TODO: implements function which validate a document against rules
    # errors = validate_document(document)
    # if errors:
    #     return None, errors
    return document, None


def collect_executable_variable_definitions(
    schema: "GraphQLSchema",
    variable_definition_nodes: List["VariableDefinitionNode"],
) -> List["ExecutableVariableDefinition"]:
    """
    Go recursively through all variable definition AST nodes to convert them as
    executable variable definition.
    :param schema: the GraphQLSchema schema instance linked to the engine
    :param variable_definition_nodes: the list of variable definition AST to
    treat
    :type schema: GraphQLSchema
    :type variable_definition_nodes: List[VariableDefinitionNode]
    :return: a list of executable variable definition
    :rtype: List[ExecutableVariableDefinition]
    """
    return [
        variable_definition_node_to_executable(
            schema, variable_definition_node
        )
        for variable_definition_node in variable_definition_nodes
    ]
