from tartiflette import Scalar

from .string import ScalarString


class ScalarId(ScalarString):
    # TODO: :-), with @relay I think.
    pass


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
    Scalar("ID", schema_name=schema_name)(ScalarId())
    return "scalar ID"
