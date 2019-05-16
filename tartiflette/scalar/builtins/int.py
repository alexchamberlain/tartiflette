from typing import Any, Union

from tartiflette import Scalar
from tartiflette.constants import UNDEFINED_VALUE
from tartiflette.language.ast import IntValueNode

_MAX_INT = 2_147_483_647
_MIN_INT = -2_147_483_648


class ScalarInt:
    """
    TODO:
    """

    def coerce_output(self, value: Any) -> int:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        return int(value)

    def coerce_input(self, value: Any) -> int:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        # ¯\_(ツ)_/¯ booleans are int: `assert isinstance(True, int) is True`
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(
                f"Int cannot represent non-integer value: < {value} >"
            )
        if not _MIN_INT <= value <= _MAX_INT:
            raise TypeError(
                "Int cannot represent non 32-bit signed integer value: "
                f"< {value} >"
            )
        return value

    def parse_literal(self, ast: "Node") -> Union[int, "UNDEFINED_VALUE"]:
        """
        TODO:
        :param ast: TODO:
        :type ast: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        if not isinstance(ast, IntValueNode):
            return UNDEFINED_VALUE

        try:
            value = int(ast.value)
            if _MIN_INT <= value <= _MAX_INT:
                return value
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
    Scalar("Int", schema_name=schema_name)(ScalarInt())
    return "scalar Int"
