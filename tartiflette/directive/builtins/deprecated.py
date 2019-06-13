from typing import Any, Callable, Dict, Optional

from tartiflette import Directive


class Deprecated:
    """
    TODO:
    """

    async def on_introspection(
        self,
        directive_args: Dict[str, Any],
        next_directive: Callable,
        introspected_element: Any,
        ctx: Optional[Dict[str, Any]],
        info: "Info",
    ):
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
        # pylint: disable=no-self-use
        introspected_element = await next_directive(
            introspected_element, ctx, info
        )

        setattr(introspected_element, "isDeprecated", True)
        setattr(
            introspected_element, "deprecationReason", directive_args["reason"]
        )

        return introspected_element


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
    Directive("deprecated", schema_name=schema_name)(Deprecated())
    return """
    directive @deprecated(
        reason: String = "Deprecated"
    ) on FIELD_DEFINITION | ENUM_VALUE
    """
