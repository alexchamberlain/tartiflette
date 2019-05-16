from typing import Any, Union

from tartiflette import Scalar
from tartiflette.constants import UNDEFINED_VALUE
from tartiflette.language.ast import BooleanValueNode


class ScalarBoolean:
    """
    TODO:
    """

    def coerce_output(self, value: Any) -> bool:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        return bool(value)

    def coerce_input(self, value: Any) -> bool:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        if not isinstance(value, bool):
            raise TypeError(
                f"Boolean cannot represent a non boolean value: < {value} >"
            )
        return value

    def parse_literal(self, ast: "Node") -> Union[bool, "UNDEFINED_VALUE"]:
        """
        TODO:
        :param ast: TODO:
        :type ast: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        return (
            ast.value if isinstance(ast, BooleanValueNode) else UNDEFINED_VALUE
        )


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
    Scalar("Boolean", schema_name=schema_name)(ScalarBoolean())
    return "scalar Boolean"
