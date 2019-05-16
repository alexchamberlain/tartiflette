from tartiflette import Directive
from tartiflette.types.exceptions.tartiflette import SkipCollection


def _include_collection(directive_args, selection):
    """
    TODO:
    :param directive_args: TODO:
    :param selection: TODO:
    :type directive_args: TODO:
    :type selection: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    if not directive_args["if"]:
        raise SkipCollection()
    return selection


class Include:
    """
    TODO:
    """

    async def on_field_collection(
        self, directive_args, next_directive, selection
    ):
        """
        TODO:
        :param directive_args: TODO:
        :param next_directive: TODO:
        :param selection: TODO:
        :type directive_args: TODO:
        :type next_directive: TODO:
        :type selection: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        return _include_collection(
            directive_args, await next_directive(selection)
        )

    async def on_fragment_spread_collection(
        self, directive_args, next_directive, selection
    ):
        """
        TODO:
        :param directive_args: TODO:
        :param next_directive: TODO:
        :param selection: TODO:
        :type directive_args: TODO:
        :type next_directive: TODO:
        :type selection: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        return _include_collection(
            directive_args, await next_directive(selection)
        )

    async def on_inline_fragment_collection(
        self, directive_args, next_directive, selection
    ):
        """
        TODO:
        :param directive_args: TODO:
        :param next_directive: TODO:
        :param selection: TODO:
        :type directive_args: TODO:
        :type next_directive: TODO:
        :type selection: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        return _include_collection(
            directive_args, await next_directive(selection)
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
    Directive("include", schema_name=schema_name)(Include())
    return "directive @include(if: Boolean!) on FIELD | FRAGMENT_SPREAD | INLINE_FRAGMENT"
