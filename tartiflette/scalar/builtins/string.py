from typing import Any, Union

from tartiflette import Scalar
from tartiflette.constants import UNDEFINED_VALUE
from tartiflette.language.ast import StringValueNode


class ScalarString:
    """
    TODO:
    """

    def coerce_output(self, value: Any) -> str:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        return str(value)

    def coerce_input(self, value: Any) -> str:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        if not isinstance(value, str):
            raise TypeError(
                f"String cannot represent a non string value: < {value} >"
            )
        return value

    def parse_literal(self, ast: "Node") -> Union[str, "UNDEFINED_VALUE"]:
        """
        TODO:
        :param ast: TODO:
        :type ast: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        return (
            ast.value if isinstance(ast, StringValueNode) else UNDEFINED_VALUE
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
    Scalar("String", schema_name=schema_name)(ScalarString())
    return "scalar String"
