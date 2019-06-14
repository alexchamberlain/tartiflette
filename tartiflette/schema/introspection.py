from functools import partial
from typing import Any, Dict, Optional

from tartiflette.types.argument import GraphQLArgument
from tartiflette.types.field import GraphQLField
from tartiflette.types.helpers import get_typename
from tartiflette.types.non_null import GraphQLNonNull


async def __schema_resolver(
    parent_result: Optional[Any],
    args: Dict[str, Any],
    ctx: Optional[Any],
    info: "ResolveInfo",
) -> "GraphQLSchema":
    """
    TODO:
    :param parent_result: TODO:
    :param args: TODO:
    :param ctx: TODO:
    :param info: TODO:
    :type parent_result: TODO:
    :type args: TODO:
    :type ctx: TODO:
    :type info: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # pylint: disable=unused-argument
    info.execution_ctx.is_introspection = True
    return info.schema


SCHEMA_ROOT_FIELD_DEFINITION = partial(
    GraphQLField,
    name="__schema",
    description="Access the current type schema of this server.",
    arguments=None,
    resolver=__schema_resolver,
)


async def __type_resolver(
    parent_result: Optional[Any],
    args: Dict[str, Any],
    ctx: Optional[Any],
    info: "ResolveInfo",
) -> str:
    """
    TODO:
    :param parent_result: TODO:
    :param args: TODO:
    :param ctx: TODO:
    :param info: TODO:
    :type parent_result: TODO:
    :type args: TODO:
    :type ctx: TODO:
    :type info: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # pylint: disable=unused-argument
    info.execution_ctx.is_introspection = True
    return info.schema.find_type(args["name"])


def prepare_type_root_field(schema: "GraphQLSchema") -> "GraphQLField":
    """
    TODO:
    :param schema: TODO:
    :type schema: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return GraphQLField(
        name="__type",
        description="Request the type information of a single type.",
        arguments={
            "name": GraphQLArgument(
                name="name",
                gql_type=GraphQLNonNull("String", schema=schema),
                schema=schema,
            )
        },
        gql_type="__Type",
        resolver=__type_resolver,
        schema=schema,
    )


async def __typename_resolver(
    parent_result: Optional[Any],
    args: Dict[str, Any],
    ctx: Optional[Any],
    info: "ResolveInfo",
) -> "GraphQLType":
    """
    TODO:
    :param parent_result: TODO:
    :param args: TODO:
    :param ctx: TODO:
    :param info: TODO:
    :type parent_result: TODO:
    :type args: TODO:
    :type ctx: TODO:
    :type info: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # pylint: disable=unused-argument
    try:
        return info.schema.find_type(get_typename(parent_result))
    except (AttributeError, KeyError):
        pass
    return info.parent_type


TYPENAME_ROOT_FIELD_DEFINITION = partial(
    GraphQLField,
    name="__typename",
    description="The name of the current Object type at runtime.",
    arguments=None,
    resolver=__typename_resolver,
)
