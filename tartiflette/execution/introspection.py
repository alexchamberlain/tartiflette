from functools import partial
from typing import Any, Dict, Optional

from tartiflette.types.field import GraphQLField


async def typename_meta_field_resolver(
    parent_result: Any,
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
    return info.parent_type.name


TYPENAME_META_FIELD_DEFINITION = partial(
    GraphQLField,
    name="__typename",
    description="The name of the current Object type at runtime.",
    arguments=None,
    resolver=typename_meta_field_resolver,
)
