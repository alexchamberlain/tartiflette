from math import isfinite
from typing import Any, Union

from tartiflette import Scalar
from tartiflette.constants import UNDEFINED_VALUE
from tartiflette.language.ast import FloatValueNode, IntValueNode


class ScalarFloat:
    """
    TODO:
    """

    def coerce_output(self, value: Any) -> float:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        return float(value)

    def coerce_input(self, value: Any) -> float:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        # ¯\_(ツ)_/¯ booleans are int: `assert isinstance(True, int) is True`
        if isinstance(value, bool) or not (
            isinstance(value, int)
            or (isinstance(value, float) and isfinite(value))
        ):
            raise TypeError(
                f"Float cannot represent non numeric value: < {value} >"
            )
        return float(value)

    def parse_literal(self, ast: "Node") -> Union[float, "UNDEFINED_VALUE"]:
        """
        TODO:
        :param ast: TODO:
        :type ast: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        if not isinstance(ast, (FloatValueNode, IntValueNode)):
            return UNDEFINED_VALUE

        try:
            return float(ast.value)
        except Exception:  # pylint: disable=broad-except
            pass
        return UNDEFINED_VALUE


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
    Scalar("Float", schema_name=schema_name)(ScalarFloat())
    return "scalar Float"
