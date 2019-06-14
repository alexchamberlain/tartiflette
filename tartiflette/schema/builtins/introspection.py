import os


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
    with open(
        os.path.join(os.path.dirname(__file__), "introspection.sdl")
    ) as file:
        return file.read()
