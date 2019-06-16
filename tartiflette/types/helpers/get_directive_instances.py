from functools import partial
from typing import Any, Dict, List, Optional


def get_callables(implementation):
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
        "callables": get_callables(directive.implementation),
        "args": {
            arg_name: directive.arguments[arg_name].default_value
            for arg_name in directive.arguments
        }
        if not args
        else args,
    }


def get_schema_directive_instances(
    directives: Dict[str, Optional[dict]], schema: "GraphQLSchema"
) -> List[Dict[str, Any]]:
    """
    TODO:
    :param directives: TODO:
    :param schema: TODO:
    :type directives: TODO:
    :type schema: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    try:
        computed_directives = []
        for directive_definition in directives:
            directive = schema.find_directive(directive_definition["name"])
            directive_dict = transform_directive(directive)

            if isinstance(directive_definition["args"], dict):
                directive_dict["args"].update(directive_definition["args"])

            computed_directives.append(directive_dict)
        return computed_directives
    except (AttributeError, KeyError, TypeError):
        pass
    return []


def get_query_directive_instances(
    execution_context: "ExecutionContext",
    directive_nodes: List["DirectiveNode"],
    info: Optional["ResolveInfo"] = None,
) -> List[Dict[str, Any]]:
    # TODO: tmp fix for cyclic imports
    from tartiflette.coercers.arguments import coerce_arguments

    try:
        computed_directives = []
        for directive_node in directive_nodes:
            directive_definition = execution_context.schema.find_directive(
                directive_node.name.value
            )
            computed_directives.append(
                transform_directive(
                    directive_definition,
                    args=partial(
                        coerce_arguments,
                        argument_definitions=directive_definition.arguments,
                        node=directive_node,
                        variable_values=execution_context.variable_values,
                        ctx=execution_context.context,
                        info=info,
                    ),
                )
            )
        return computed_directives
    except Exception:  # pylint: disable=broad-e
        # TODO: what shoud we do here? lets propagate the error to be catch
        # and added to the execution context errors?
        pass
    return []
