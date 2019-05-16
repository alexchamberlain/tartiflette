from datetime import datetime
from typing import Union

from tartiflette import Scalar
from tartiflette.constants import UNDEFINED_VALUE
from tartiflette.language.ast import StringValueNode


class ScalarDate:
    """
    TODO:
    """

    def coerce_output(self, value: datetime) -> str:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        return value.isoformat().split("T")[0]

    def coerce_input(self, value: str) -> datetime:
        """
        TODO:
        :param value: TODO:
        :type value: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        return datetime.strptime(value, "%Y-%m-%d")

    def parse_literal(self, ast: "Node") -> Union[datetime, "UNDEFINED_VALUE"]:
        """
        TODO:
        :param ast: TODO:
        :type ast: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=no-self-use
        if not isinstance(ast, StringValueNode):
            return UNDEFINED_VALUE

        try:
            return datetime.strptime(ast.value, "%Y-%m-%d")
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
    Scalar("Date", schema_name=schema_name)(ScalarDate())
    return "scalar Date"
