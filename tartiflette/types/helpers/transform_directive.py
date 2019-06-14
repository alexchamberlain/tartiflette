def _get_callables(implementation):
    """
    TODO:
    :param implementation: TODO:
    :type implementation: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return {
        key: getattr(implementation, key)
        for key in dir(implementation)
        if key.startswith("on_")
    }


def transform_directive(directive, args=None):
    """
    TODO:
    :param directive: TODO:
    :param args: TODO:
    :type directive: TODO:
    :type args: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return {
        "callables": _get_callables(directive.implementation),
        "args": {
            arg_name: directive.arguments[arg_name].default_value
            for arg_name in directive.arguments
        }
        if not args
        else args,
    }
