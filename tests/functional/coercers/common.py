from tartiflette import Directive, Scalar
from tartiflette.scalar.builtins.boolean import ScalarBoolean
from tartiflette.scalar.builtins.float import ScalarFloat
from tartiflette.scalar.builtins.int import ScalarInt
from tartiflette.scalar.builtins.string import ScalarString


class BooleanScalar(ScalarBoolean):
    pass


class FloatScalar(ScalarFloat):
    pass


class IntScalar(ScalarInt):
    pass


class StringScalar(ScalarString):
    pass


class DebugDirective:
    async def on_argument_execution(
        self,
        directive_args,
        next_directive,
        argument_definition,
        args,
        ctx,
        info,
    ):
        result = await next_directive(argument_definition, args, ctx, info)
        # print("@adebug:", directive_args.get("message"))
        return result

    async def on_post_input_coercion(
        self,
        directive_args,
        next_directive,
        value,
        argument_definition,
        ctx,
        info,
    ):
        result = await next_directive(value, argument_definition, ctx, info)
        # print("@idebug:", directive_args.get("message"))
        return result


class LowercaseDirective:
    async def on_argument_execution(
        self,
        directive_args,
        next_directive,
        argument_definition,
        args,
        ctx,
        info,
    ):
        result = await next_directive(argument_definition, args, ctx, info)
        if isinstance(result, str):
            return result.lower()
        if isinstance(result, list):
            return [
                value.lower() if isinstance(value, str) else value
                for value in result
            ]
        return result

    async def on_post_input_coercion(
        self,
        directive_args,
        next_directive,
        value,
        argument_definition,
        ctx,
        info,
    ):
        result = await next_directive(value, argument_definition, ctx, info)
        if isinstance(result, str):
            return result.lower()
        if isinstance(result, list):
            return [
                value.lower() if isinstance(value, str) else value
                for value in result
            ]
        return result


class IncrementDirective:
    async def on_argument_execution(
        self,
        directive_args,
        next_directive,
        argument_definition,
        args,
        ctx,
        info,
    ):
        result = await next_directive(argument_definition, args, ctx, info)
        if isinstance(result, (int, float)):
            return result + directive_args["step"]
        if isinstance(result, list):
            return [
                value + directive_args["step"]
                if isinstance(value, (int, float))
                else value
                for value in result
            ]
        return result

    async def on_post_input_coercion(
        self,
        directive_args,
        next_directive,
        value,
        argument_definition,
        ctx,
        info,
    ):
        result = await next_directive(value, argument_definition, ctx, info)
        if isinstance(result, (int, float)):
            return result + directive_args["step"]
        if isinstance(result, list):
            return [
                value + directive_args["step"]
                if isinstance(value, (int, float))
                else value
                for value in result
            ]
        return result


class ConcatenateDirective:
    async def on_argument_execution(
        self,
        directive_args,
        next_directive,
        argument_definition,
        args,
        ctx,
        info,
    ):
        result = await next_directive(argument_definition, args, ctx, info)
        return (
            result + directive_args["with"]
            if isinstance(result, str)
            else result
        )

    async def on_post_input_coercion(
        self,
        directive_args,
        next_directive,
        value,
        argument_definition,
        ctx,
        info,
    ):
        result = await next_directive(value, argument_definition, ctx, info)
        return (
            result + directive_args["with"]
            if isinstance(result, str)
            else result
        )


class MapToValueDirective:
    async def on_argument_execution(
        self,
        directive_args,
        next_directive,
        argument_definition,
        args,
        ctx,
        info,
    ):
        await next_directive(argument_definition, args, ctx, info)
        return directive_args["newValue"]

    async def on_post_input_coercion(
        self,
        directive_args,
        next_directive,
        value,
        argument_definition,
        ctx,
        info,
    ):
        await next_directive(value, argument_definition, ctx, info)
        return directive_args["newValue"]


async def resolve_unwrapped_field(parent, args, ctx, info):
    if "param" in args:
        return f"SUCCESS-{args['param']}"
    return "SUCCESS"


async def resolve_list_field(parent, args, ctx, info):
    if "param" in args:
        return "SUCCESS-[{}]".format(
            str(args["param"])
            if not isinstance(args["param"], list)
            else "-".join([str(item) for item in args["param"]])
        )
    return "SUCCESS"


async def resolve_input_object_field(parent, args, ctx, info):
    if "param" in args:
        if args["param"] is None:
            return "SUCCESS-None"
        # TODO: remove this condition when the `validate` function is available
        # in order to highlight some errors on literal coercion especially on
        # InputObject with NonNull InputFields with null value specified as
        # default value
        if isinstance(args["param"], dict):
            if not args["param"]:
                return "SUCCESS-{}"
            return "SUCCESS-{}".format(
                "-".join(
                    [
                        "[{}:{}]".format(
                            str(arg_name),
                            str(
                                arg_values
                                if not isinstance(arg_values, list)
                                else "-".join([str(arg) for arg in arg_values])
                            ),
                        )
                        for arg_name, arg_values in args["param"].items()
                    ]
                )
            )
    return "SUCCESS"


def bake(schema_name, config):
    Scalar("Boolean", schema_name="coercion")(BooleanScalar())
    Scalar("Float", schema_name="coercion")(FloatScalar())
    Scalar("Int", schema_name="coercion")(IntScalar())
    Scalar("String", schema_name="coercion")(StringScalar())
    Directive("debug", schema_name="coercion")(DebugDirective())
    Directive("lowercase", schema_name="coercion")(LowercaseDirective())
    Directive("increment", schema_name="coercion")(IncrementDirective())
    Directive("concatenate", schema_name="coercion")(ConcatenateDirective())
    Directive("mapToValue", schema_name="coercion")(MapToValueDirective())
    return ""
