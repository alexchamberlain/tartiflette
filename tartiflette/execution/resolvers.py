from typing import Any, Dict, Optional, Union


async def default_field_resolver(
    parent_result: Optional[Any],
    args: Dict[str, Any],
    ctx: Optional[Any],
    info: "ResolveInfo",
) -> Any:
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
        return getattr(parent_result, info.field_name)
    except AttributeError:
        pass

    try:
        return parent_result[info.field_name]
    except (KeyError, TypeError):
        pass
    return None


async def default_type_resolver(
    result: Any,
    ctx: Optional[Any],
    info: "ResolverInfo",
    abstract_type: Union["GraphQLInterfaceType", "GraphQLUnionType"],
) -> str:
    """
    TODO:
    :param result: TODO:
    :param ctx: TODO:
    :param info: TODO:
    :type result: TODO:
    :type ctx: TODO:
    :type info: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # pylint: disable=unused-argument
    try:
        return result["_typename"]
    except (KeyError, TypeError):
        pass

    try:
        return result._typename  # pylint: disable=protected-access
    except AttributeError:
        pass

    return result.__class__.__name__
