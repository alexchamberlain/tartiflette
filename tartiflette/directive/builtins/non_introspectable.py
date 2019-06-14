from typing import Any, Callable, Dict, Optional

from tartiflette import Directive


class NonIntrospectable:
    """
    TODO:
    """

    async def on_introspection(
        self,
        directive_args: Dict[str, Any],
        next_directive: Callable,
        introspected_element: Any,
        ctx: Optional[Dict[str, Any]],
        info: "ResolveInfo",
    ) -> None:
        """
        TODO:
        :param directive_args: TODO:
        :param next_directive: TODO:
        :param introspected_element: TODO:
        :param ctx: TODO:
        :param info: TODO:
        :type directive_args: TODO:
        :type next_directive: TODO:
        :type introspected_element: TODO:
        :type ctx: TODO:
        :type info: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=unused-argument
        return None


class NonIntrospectableDeprecated:
    async def on_introspection(
        self,
        directive_args: Dict[str, Any],
        next_directive: Callable,
        introspected_element: Any,
        ctx: Optional[Dict[str, Any]],
        info: "ResolveInfo",
    ) -> None:
        """
        TODO:
        :param directive_args: TODO:
        :param next_directive: TODO:
        :param introspected_element: TODO:
        :param ctx: TODO:
        :param info: TODO:
        :type directive_args: TODO:
        :type next_directive: TODO:
        :type introspected_element: TODO:
        :type ctx: TODO:
        :type info: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=unused-argument
        print(
            "@non_introspectable is deprecated, please use @nonIntrospectable, will be removed in 0.12.0"
        )
        return None


def bake(schema_name, config):
    """
    TODO:
    :param schema_name: TODO:
    :param config: TODO:
    :type schema_name: TODO:
    :type config: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    # pylint: disable=unused-argument
    Directive("nonIntrospectable", schema_name=schema_name)(
        NonIntrospectable()
    )
    Directive("non_introspectable", schema_name=schema_name)(
        NonIntrospectableDeprecated()
    )
    return """
    directive @nonIntrospectable on FIELD_DEFINITION
    directive @non_introspectable on FIELD_DEFINITION
    """
