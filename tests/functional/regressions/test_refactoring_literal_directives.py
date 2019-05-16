import pytest

from tartiflette import Directive, Resolver, create_engine

_SDL = """
directive @lower on ENUM_VALUE | INPUT_FIELD_DEFINITION
directive @increment(step: Int = 1) on INPUT_FIELD_DEFINITION
directive @mapToValue(value: String!) on ENUM_VALUE

enum MyEnum {
  ENUM_1 @mapToValue(value: "ENUM_1_1") @lower
  ENUM_2 @lower @mapToValue(value: "ENUM_2_2")
  ENUM_3
}

input ObjectInput {
  intParam: Int @increment(step: 2)
  listIntParam: [Int]
  floatParam: Float @increment(step: 2)
  listFloatParam: [Float]
  booleanParam: Boolean
  listBooleanParam: [Boolean]
  stringParam: String @lower
  listStringParam: [String]
  enumParam: MyEnum @lower
  listEnumParam: [MyEnum]
}

input NonNullWrapperObjectInput {
  intParam: Int
  listIntParam: [Int]!
  floatParam: Float
  listFloatParam: [Float]!
  booleanParam: Boolean
  listBooleanParam: [Boolean]!
  stringParam: String
  listStringParam: [String]!
  enumParam: MyEnum
  listEnumParam: [MyEnum]!
}

input NonNullInnerObjectInput {
  intParam: Int
  listIntParam: [Int!]
  floatParam: Float
  listFloatParam: [Float!]
  booleanParam: Boolean
  listBooleanParam: [Boolean!]
  stringParam: String
  listStringParam: [String!]
  enumParam: MyEnum
  listEnumParam: [MyEnum!]
}

input NonNullObjectInput {
  intParam: Int!
  listIntParam: [Int!]!
  floatParam: Float!
  listFloatParam: [Float!]!
  booleanParam: Boolean!
  listBooleanParam: [Boolean!]!
  stringParam: String!
  listStringParam: [String!]!
  enumParam: MyEnum!
  listEnumParam: [MyEnum!]!
}

input ObjectInputWithDefault {
  intParam: Int = 10
  listIntParam: [Int] = [20, 21]
  floatParam: Float = null
  listFloatParam: [Float] = [23456.789e2, 12.4, -1, 0.2e1]
  booleanParam: Boolean = false
  listBooleanParam: [Boolean] = [false, true]
  stringParam: String = "defaultValue"
  listStringParam: [String] = ["firstDefaultValue", "secondDefaultValue"]
  enumParam: MyEnum = ENUM_2
  listEnumParam: [MyEnum] = [ENUM_2, ENUM_3]
}

type AType {
  aTypeField: String
}

type Query {
  intField(intParam: Int): String
  floatField(floatParam: Float): String
  booleanField(booleanParam: Boolean): String
  stringField(stringParam: String): String
  enumField(enumParam: MyEnum): String

  nonNullIntField(intParam: Int!): String
  nonNullFloatField(floatParam: Float!): String
  nonNullBooleanField(booleanParam: Boolean!): String
  nonNullStringField(stringParam: String!): String
  nonNullEnumField(enumParam: MyEnum!): String

  listIntField(listIntParam: [Int]): String
  listFloatField(listFloatParam: [Float]): String
  listBooleanField(listBooleanParam: [Boolean]): String
  listStringField(listStringParam: [String]): String
  listEnumField(listEnumParam: [MyEnum]): String

  nonNullListIntField(listIntParam: [Int]!): String
  nonNullListFloatField(listFloatParam: [Float]!): String
  nonNullListBooleanField(listBooleanParam: [Boolean]!): String
  nonNullListStringField(listStringParam: [String]!): String
  nonNullListEnumField(listEnumParam: [MyEnum]!): String

  objectField(objectParam: ObjectInput): String
}
"""


@pytest.fixture(scope="module")
async def ttftt_engine():
    @Resolver(
        "Query.intField", schema_name="test_refactoring_literal_directives"
    )
    @Resolver(
        "Query.nonNullIntField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_int_field(parent, args, ctx, info):
        if "intParam" in args:
            return f"SUCCESS-{args['intParam']}"
        return "SUCCESS"

    @Resolver(
        "Query.floatField", schema_name="test_refactoring_literal_directives"
    )
    @Resolver(
        "Query.nonNullFloatField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_float_field(parent, args, ctx, info):
        if "floatParam" in args:
            return f"SUCCESS-{args['floatParam']}"
        return "SUCCESS"

    @Resolver(
        "Query.booleanField", schema_name="test_refactoring_literal_directives"
    )
    @Resolver(
        "Query.nonNullBooleanField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_boolean_field(parent, args, ctx, info):
        if "booleanParam" in args:
            return f"SUCCESS-{args['booleanParam']}"
        return "SUCCESS"

    @Resolver(
        "Query.stringField", schema_name="test_refactoring_literal_directives"
    )
    @Resolver(
        "Query.nonNullStringField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_string_field(parent, args, ctx, info):
        if "stringParam" in args:
            return f"SUCCESS-{args['stringParam']}"
        return "SUCCESS"

    @Resolver(
        "Query.enumField", schema_name="test_refactoring_literal_directives"
    )
    @Resolver(
        "Query.nonNullEnumField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_enum_field(parent, args, ctx, info):
        if "enumParam" in args:
            return f"SUCCESS-{args['enumParam']}"
        return "SUCCESS"

    @Resolver(
        "Query.listIntField", schema_name="test_refactoring_literal_directives"
    )
    @Resolver(
        "Query.nonNullListIntField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_list_int_field(parent, args, ctx, info):
        if "listIntParam" in args:
            return "SUCCESS-{}".format(
                str(args["listIntParam"])
                if not isinstance(args["listIntParam"], list)
                else "-".join([str(item) for item in args["listIntParam"]])
            )
        return "SUCCESS"

    @Resolver(
        "Query.listFloatField",
        schema_name="test_refactoring_literal_directives",
    )
    @Resolver(
        "Query.nonNullListFloatField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_list_float_field(parent, args, ctx, info):
        if "listFloatParam" in args:
            return "SUCCESS-{}".format(
                str(args["listFloatParam"])
                if not isinstance(args["listFloatParam"], list)
                else "-".join([str(item) for item in args["listFloatParam"]])
            )
        return "SUCCESS"

    @Resolver(
        "Query.listBooleanField",
        schema_name="test_refactoring_literal_directives",
    )
    @Resolver(
        "Query.nonNullListBooleanField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_list_boolean_field(parent, args, ctx, info):
        if "listBooleanParam" in args:
            return "SUCCESS-{}".format(
                str(args["listBooleanParam"])
                if not isinstance(args["listBooleanParam"], list)
                else "-".join([str(item) for item in args["listBooleanParam"]])
            )
        return "SUCCESS"

    @Resolver(
        "Query.listStringField",
        schema_name="test_refactoring_literal_directives",
    )
    @Resolver(
        "Query.nonNullListStringField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_list_string_field(parent, args, ctx, info):
        if "listStringParam" in args:
            return "SUCCESS-{}".format(
                str(args["listStringParam"])
                if not isinstance(args["listStringParam"], list)
                else "-".join([str(item) for item in args["listStringParam"]])
            )
        return "SUCCESS"

    @Resolver(
        "Query.listEnumField",
        schema_name="test_refactoring_literal_directives",
    )
    @Resolver(
        "Query.nonNullListEnumField",
        schema_name="test_refactoring_literal_directives",
    )
    async def resolve_query_list_enum_field(parent, args, ctx, info):
        if "listEnumParam" in args:
            return "SUCCESS-{}".format(
                str(args["listEnumParam"])
                if not isinstance(args["listEnumParam"], list)
                else "-".join([str(item) for item in args["listEnumParam"]])
            )
        return "SUCCESS"

    @Resolver(
        "Query.objectField", schema_name="test_refactoring_literal_directives"
    )
    async def resolve_query_object_field(parent, args, ctx, info):
        if "objectParam" in args:
            if args["objectParam"] is None:
                return "SUCCESS-None"
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
                        for arg_name, arg_values in args["objectParam"].items()
                    ]
                )
            )
        return "SUCCESS"

    @Directive("lower", schema_name="test_refactoring_literal_directives")
    class LowerDirective:
        async def on_post_input_coercion(
            self,
            directive_args,
            next_directive,
            value,
            argument_definition,
            ctx,
            info,
        ):
            if isinstance(value, str):
                value = value.lower()
            return await next_directive(value, argument_definition, ctx, info)

    @Directive("increment", schema_name="test_refactoring_literal_directives")
    class IncrementDirective:
        async def on_post_input_coercion(
            self,
            directive_args,
            next_directive,
            value,
            argument_definition,
            ctx,
            info,
        ):
            if value is not None:
                value = value + directive_args["step"]
            return await next_directive(value, argument_definition, ctx, info)

    @Directive("mapToValue", schema_name="test_refactoring_literal_directives")
    class MapToValueDirective:
        async def on_post_input_coercion(
            self,
            directive_args,
            next_directive,
            value,
            argument_definition,
            ctx,
            info,
        ):
            value = directive_args["value"]
            return await next_directive(value, argument_definition, ctx, info)

    return await create_engine(
        _SDL, schema_name="test_refactoring_literal_directives"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        (
            """
            query IntParamWithDefault($value: Int = null) {
              intField(intParam: $value)
            }
            """,
            None,
            {"data": {"intField": "SUCCESS-None"}},
        ),
        (
            """
            query IntParamWithDefault($value: Int = 20) {
              intField(intParam: $value)
            }
            """,
            None,
            {"data": {"intField": "SUCCESS-20"}},
        ),
        (
            """
            query NonNullIntParamWithDefault($value: Int! = null) {
              nonNullIntField(intParam: $value)
            }
            """,
            None,
            {"data": {"nonNullIntField": "SUCCESS"}},
        ),
        (
            """
            query NonNullIntParamWithDefault($value: Int! = 20) {
              nonNullIntField(intParam: $value)
            }
            """,
            None,
            {"data": {"nonNullIntField": "SUCCESS-20"}},
        ),
    ],
)
async def test_refactoring_literal_directives_int(
    ttftt_engine, query, variables, expected
):
    assert await ttftt_engine.execute(query, variables=variables) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        (
            """
            query FloatParamWithDefault($value: Float = null) {
              floatField(floatParam: $value)
            }
            """,
            None,
            {"data": {"floatField": "SUCCESS-None"}},
        ),
        (
            """
            query FloatParamWithDefault($value: Float = 23456.789e2) {
              floatField(floatParam: $value)
            }
            """,
            None,
            {"data": {"floatField": "SUCCESS-2345678.9"}},
        ),
        (
            """
            query NonNullFloatParamWithDefault($value: Float! = null) {
              nonNullFloatField(floatParam: $value)
            }
            """,
            None,
            {"data": {"nonNullFloatField": "SUCCESS"}},
        ),
        (
            """
            query NonNullFloatParamWithDefault($value: Float! = 23456.789e2) {
              nonNullFloatField(floatParam: $value)
            }
            """,
            None,
            {"data": {"nonNullFloatField": "SUCCESS-2345678.9"}},
        ),
    ],
)
async def test_refactoring_literal_directives_float(
    ttftt_engine, query, variables, expected
):
    assert await ttftt_engine.execute(query, variables=variables) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        (
            """
            query BooleanParamWithDefault($value: Boolean = null) {
              booleanField(booleanParam: $value)
            }
            """,
            None,
            {"data": {"booleanField": "SUCCESS-None"}},
        ),
        (
            """
            query BooleanParamWithDefault($value: Boolean = false) {
              booleanField(booleanParam: $value)
            }
            """,
            None,
            {"data": {"booleanField": "SUCCESS-False"}},
        ),
        (
            """
            query NonNullBooleanParamWithDefault($value: Boolean! = null) {
              nonNullBooleanField(booleanParam: $value)
            }
            """,
            None,
            {"data": {"nonNullBooleanField": "SUCCESS"}},
        ),
        (
            """
            query NonNullBooleanParamWithDefault($value: Boolean! = false) {
              nonNullBooleanField(booleanParam: $value)
            }
            """,
            None,
            {"data": {"nonNullBooleanField": "SUCCESS-False"}},
        ),
    ],
)
async def test_refactoring_literal_directives_boolean(
    ttftt_engine, query, variables, expected
):
    assert await ttftt_engine.execute(query, variables=variables) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        (
            """
            query StringParamWithDefault($value: String = null) {
              stringField(stringParam: $value)
            }
            """,
            None,
            {"data": {"stringField": "SUCCESS-None"}},
        ),
        (
            """
            query StringParamWithDefault($value: String = "defaultValue") {
              stringField(stringParam: $value)
            }
            """,
            None,
            {"data": {"stringField": "SUCCESS-defaultValue"}},
        ),
        (
            """
            query NonNullStringParamWithDefault($value: String! = null) {
              nonNullStringField(stringParam: $value)
            }
            """,
            None,
            {"data": {"nonNullStringField": "SUCCESS"}},
        ),
        (
            """
            query NonNullStringParamWithDefault($value: String! = "defaultValue") {
              nonNullStringField(stringParam: $value)
            }
            """,
            None,
            {"data": {"nonNullStringField": "SUCCESS-defaultValue"}},
        ),
    ],
)
async def test_refactoring_literal_directives_string(
    ttftt_engine, query, variables, expected
):
    assert await ttftt_engine.execute(query, variables=variables) == expected


# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "query,variables,expected",
#     [
#         (
#             """
#             query EnumParamWithDefault($value: MyEnum = ENUM_2) {
#               enumField(enumParam: $value)
#             }
#             """,
#             None,
#             {"data": {"enumField": "SUCCESS-ENUM_2"}},
#         ),
#         (
#             """
#             query EnumParam {
#               enumField(enumParam: ENUM_2)
#             }
#             """,
#             None,
#             {"data": {"enumField": "SUCCESS-ENUM_2"}},
#         ),
#     ],
# )
# async def test_refactoring_literal_directives_enum(
#     ttftt_engine, query, variables, expected
# ):
#     assert await ttftt_engine.execute(query, variables=variables) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        (
            """
            query ListIntParamWithDefault($values: [Int] = null) {
              listIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"listIntField": "SUCCESS-None"}},
        ),
        (
            """
            query ListIntParamWithDefault($values: [Int] = [20, 21, null]) {
              listIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"listIntField": "SUCCESS-20-21-None"}},
        ),
        (
            """
            query ListIntParamWithDefault($values: [Int] = [20, 21]) {
              listIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"listIntField": "SUCCESS-20-21"}},
        ),
        (
            """
            query NonNullListIntParamWithDefault($values: [Int]! = null) {
              nonNullListIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListIntField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListIntParamWithDefault($values: [Int]! = [20, 21, null]) {
              nonNullListIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListIntField": "SUCCESS-20-21-None"}},
        ),
        (
            """
            query NonNullListIntParamWithDefault($values: [Int]! = [20, 21]) {
              nonNullListIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListIntField": "SUCCESS-20-21"}},
        ),
        (
            """
            query ListIntParamWithDefault($values: [Int!] = null) {
              listIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"listIntField": "SUCCESS-None"}},
        ),
        (
            """
            query ListIntParamWithDefault($values: [Int!] = [20, 21, null]) {
              listIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"listIntField": "SUCCESS"}},
        ),
        (
            """
            query ListIntParamWithDefault($values: [Int!] = [20, 21]) {
              listIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"listIntField": "SUCCESS-20-21"}},
        ),
        (
            """
            query NonNullListIntParamWithDefault($values: [Int!]! = null) {
              nonNullListIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListIntField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListIntParamWithDefault($values: [Int!]! = [20, 21, null]) {
              nonNullListIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListIntField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListIntParamWithDefault($values: [Int!]! = [20, 21]) {
              nonNullListIntField(listIntParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListIntField": "SUCCESS-20-21"}},
        ),
    ],
)
async def test_refactoring_literal_directives_list_int(
    ttftt_engine, query, variables, expected
):
    assert await ttftt_engine.execute(query, variables=variables) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        (
            """
            query ListFloatParamWithDefault($values: [Float] = null) {
              listFloatField(listFloatParam: $values)
            }
            """,
            None,
            {"data": {"listFloatField": "SUCCESS-None"}},
        ),
        (
            """
            query ListFloatParamWithDefault($values: [Float] = [23456.789e2, 12.4, -1, 0.2e1, null]) {
              listFloatField(listFloatParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "listFloatField": "SUCCESS-2345678.9-12.4--1.0-2.0-None"
                }
            },
        ),
        (
            """
            query ListFloatParamWithDefault($values: [Float] = [23456.789e2, 12.4, -1, 0.2e1]) {
              listFloatField(listFloatParam: $values)
            }
            """,
            None,
            {"data": {"listFloatField": "SUCCESS-2345678.9-12.4--1.0-2.0"}},
        ),
        (
            """
            query NonNullListFloatParamWithDefault($values: [Float]! = null) {
              nonNullListFloatField(listFloatParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListFloatField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListFloatParamWithDefault($values: [Float]! = [23456.789e2, 12.4, -1, 0.2e1, null]) {
              nonNullListFloatField(listFloatParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "nonNullListFloatField": "SUCCESS-2345678.9-12.4--1.0-2.0-None"
                }
            },
        ),
        (
            """
            query NonNullListFloatParamWithDefault($values: [Float]! = [23456.789e2, 12.4, -1, 0.2e1]) {
              nonNullListFloatField(listFloatParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "nonNullListFloatField": "SUCCESS-2345678.9-12.4--1.0-2.0"
                }
            },
        ),
        (
            """
            query ListFloatParamWithDefault($values: [Float!] = null) {
              listFloatField(listFloatParam: $values)
            }
            """,
            None,
            {"data": {"listFloatField": "SUCCESS-None"}},
        ),
        (
            """
            query ListFloatParamWithDefault($values: [Float!] = [23456.789e2, 12.4, -1, 0.2e1, null]) {
              listFloatField(listFloatParam: $values)
            }
            """,
            None,
            {"data": {"listFloatField": "SUCCESS"}},
        ),
        (
            """
            query ListFloatParamWithDefault($values: [Float!] = [23456.789e2, 12.4, -1, 0.2e1]) {
              listFloatField(listFloatParam: $values)
            }
            """,
            None,
            {"data": {"listFloatField": "SUCCESS-2345678.9-12.4--1.0-2.0"}},
        ),
        (
            """
            query NonNullListFloatParamWithDefault($values: [Float!]! = null) {
              nonNullListFloatField(listFloatParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListFloatField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListFloatParamWithDefault($values: [Float!]! = [23456.789e2, 12.4, -1, 0.2e1, null]) {
              nonNullListFloatField(listFloatParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListFloatField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListFloatParamWithDefault($values: [Float!]! = [23456.789e2, 12.4, -1, 0.2e1]) {
              nonNullListFloatField(listFloatParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "nonNullListFloatField": "SUCCESS-2345678.9-12.4--1.0-2.0"
                }
            },
        ),
    ],
)
async def test_refactoring_literal_directives_list_float(
    ttftt_engine, query, variables, expected
):
    assert await ttftt_engine.execute(query, variables=variables) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        (
            """
            query ListBooleanParamWithDefault($values: [Boolean] = null) {
              listBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"listBooleanField": "SUCCESS-None"}},
        ),
        (
            """
            query ListBooleanParamWithDefault($values: [Boolean] = [false, true, null]) {
              listBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"listBooleanField": "SUCCESS-False-True-None"}},
        ),
        (
            """
            query ListBooleanParamWithDefault($values: [Boolean] = [false, true]) {
              listBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"listBooleanField": "SUCCESS-False-True"}},
        ),
        (
            """
            query NonNullListBooleanParamWithDefault($values: [Boolean]! = null) {
              nonNullListBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListBooleanField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListBooleanParamWithDefault($values: [Boolean]! = [false, true, null]) {
              nonNullListBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListBooleanField": "SUCCESS-False-True-None"}},
        ),
        (
            """
            query NonNullListBooleanParamWithDefault($values: [Boolean]! = [false, true]) {
              nonNullListBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListBooleanField": "SUCCESS-False-True"}},
        ),
        (
            """
            query ListBooleanParamWithDefault($values: [Boolean!] = null) {
              listBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"listBooleanField": "SUCCESS-None"}},
        ),
        (
            """
            query ListBooleanParamWithDefault($values: [Boolean!] = [false, true, null]) {
              listBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"listBooleanField": "SUCCESS"}},
        ),
        (
            """
            query ListBooleanParamWithDefault($values: [Boolean!] = [false, true]) {
              listBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"listBooleanField": "SUCCESS-False-True"}},
        ),
        (
            """
            query NonNullListBooleanParamWithDefault($values: [Boolean!]! = null) {
              nonNullListBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListBooleanField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListBooleanParamWithDefault($values: [Boolean!]! = [false, true, null]) {
              nonNullListBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListBooleanField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListBooleanParamWithDefault($values: [Boolean!]! = [false, true]) {
              nonNullListBooleanField(listBooleanParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListBooleanField": "SUCCESS-False-True"}},
        ),
    ],
)
async def test_refactoring_literal_directives_list_boolean(
    ttftt_engine, query, variables, expected
):
    assert await ttftt_engine.execute(query, variables=variables) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        (
            """
            query ListStringParamWithDefault($values: [String] = null) {
              listStringField(listStringParam: $values)
            }
            """,
            None,
            {"data": {"listStringField": "SUCCESS-None"}},
        ),
        (
            """
            query ListStringParamWithDefault($values: [String] = ["firstDefaultValue", "secondDefaultValue", null]) {
              listStringField(listStringParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "listStringField": "SUCCESS-firstDefaultValue-secondDefaultValue-None"
                }
            },
        ),
        (
            """
            query ListStringParamWithDefault($values: [String] = ["firstDefaultValue", "secondDefaultValue"]) {
              listStringField(listStringParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "listStringField": "SUCCESS-firstDefaultValue-secondDefaultValue"
                }
            },
        ),
        (
            """
            query NonNullListStringParamWithDefault($values: [String]! = null) {
              nonNullListStringField(listStringParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListStringField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListStringParamWithDefault($values: [String]! = ["firstDefaultValue", "secondDefaultValue", null]) {
              nonNullListStringField(listStringParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "nonNullListStringField": "SUCCESS-firstDefaultValue-secondDefaultValue-None"
                }
            },
        ),
        (
            """
            query NonNullListStringParamWithDefault($values: [String]! = ["firstDefaultValue", "secondDefaultValue"]) {
              nonNullListStringField(listStringParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "nonNullListStringField": "SUCCESS-firstDefaultValue-secondDefaultValue"
                }
            },
        ),
        (
            """
            query ListStringParamWithDefault($values: [String!] = null) {
              listStringField(listStringParam: $values)
            }
            """,
            None,
            {"data": {"listStringField": "SUCCESS-None"}},
        ),
        (
            """
            query ListStringParamWithDefault($values: [String!] = ["firstDefaultValue", "secondDefaultValue", null]) {
              listStringField(listStringParam: $values)
            }
            """,
            None,
            {"data": {"listStringField": "SUCCESS"}},
        ),
        (
            """
            query ListStringParamWithDefault($values: [String!] = ["firstDefaultValue", "secondDefaultValue"]) {
              listStringField(listStringParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "listStringField": "SUCCESS-firstDefaultValue-secondDefaultValue"
                }
            },
        ),
        (
            """
            query NonNullListStringParamWithDefault($values: [String!]! = null) {
              nonNullListStringField(listStringParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListStringField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListStringParamWithDefault($values: [String!]! = ["firstDefaultValue", "secondDefaultValue", null]) {
              nonNullListStringField(listStringParam: $values)
            }
            """,
            None,
            {"data": {"nonNullListStringField": "SUCCESS"}},
        ),
        (
            """
            query NonNullListStringParamWithDefault($values: [String!]! = ["firstDefaultValue", "secondDefaultValue"]) {
              nonNullListStringField(listStringParam: $values)
            }
            """,
            None,
            {
                "data": {
                    "nonNullListStringField": "SUCCESS-firstDefaultValue-secondDefaultValue"
                }
            },
        ),
    ],
)
async def test_refactoring_literal_directives_list_string(
    ttftt_engine, query, variables, expected
):
    assert await ttftt_engine.execute(query, variables=variables) == expected


# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "query,variables,expected",
#     [
#         (
#             """
#             query ListEnumParamWithDefault($values: [MyEnum] = null) {
#               listEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"listEnumField": "SUCCESS-None"}},
#         ),
#         (
#             """
#             query ListEnumParamWithDefault($values: [MyEnum] = [ENUM_2, ENUM_3, null]) {
#               listEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"listEnumField": "SUCCESS-ENUM_2-ENUM_3-None"}},
#         ),
#         (
#             """
#             query ListEnumParamWithDefault($values: [MyEnum] = [ENUM_2, ENUM_3]) {
#               listEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"listEnumField": "SUCCESS-ENUM_2-ENUM_3"}},
#         ),
#         (
#             """
#             query NonNullListEnumParamWithDefault($values: [MyEnum]! = null) {
#               nonNullListEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"nonNullListEnumField": "SUCCESS"}},
#         ),
#         (
#             """
#             query NonNullListEnumParamWithDefault($values: [MyEnum]! = [ENUM_2, ENUM_3, null]) {
#               nonNullListEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"nonNullListEnumField": "SUCCESS-ENUM_2-ENUM_3-None"}},
#         ),
#         (
#             """
#             query NonNullListEnumParamWithDefault($values: [MyEnum]! = [ENUM_2, ENUM_3]) {
#               nonNullListEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"nonNullListEnumField": "SUCCESS-ENUM_2-ENUM_3"}},
#         ),
#         (
#             """
#             query ListEnumParamWithDefault($values: [MyEnum!] = null) {
#               listEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"listEnumField": "SUCCESS-None"}},
#         ),
#         (
#             """
#             query ListEnumParamWithDefault($values: [MyEnum!] = [ENUM_2, ENUM_3, null]) {
#               listEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"listEnumField": "SUCCESS"}},
#         ),
#         (
#             """
#             query ListEnumParamWithDefault($values: [MyEnum!] = [ENUM_2, ENUM_3]) {
#               listEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"listEnumField": "SUCCESS-ENUM_2-ENUM_3"}},
#         ),
#         (
#             """
#             query NonNullListEnumParamWithDefault($values: [MyEnum!]! = null) {
#               nonNullListEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"nonNullListEnumField": "SUCCESS"}},
#         ),
#         (
#             """
#             query NonNullListEnumParamWithDefault($values: [MyEnum!]! = [ENUM_2, ENUM_3, null]) {
#               nonNullListEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"nonNullListEnumField": "SUCCESS"}},
#         ),
#         (
#             """
#             query NonNullListEnumParamWithDefault($values: [MyEnum!]! = [ENUM_2, ENUM_3]) {
#               nonNullListEnumField(listEnumParam: $values)
#             }
#             """,
#             None,
#             {"data": {"nonNullListEnumField": "SUCCESS-ENUM_2-ENUM_3"}},
#         ),
#     ],
# )
# async def test_refactoring_literal_directives_list_enum(
#     ttftt_engine, query, variables, expected
# ):
#     assert await ttftt_engine.execute(query, variables=variables) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        # ObjectInput
        (
            """
            query ObjectParam($value: ObjectInput = null) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {"data": {"objectField": "SUCCESS-None"}},
        ),
        (
            """
            query ObjectParam($value: ObjectInput! = null) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {"data": {"objectField": "SUCCESS"}},
        ),
        (
            """
            query ObjectParamWithDefault($value: ObjectInput = {
              intParam: null,
              listIntParam: null,
              floatParam: null,
              listFloatParam: null,
              booleanParam: null,
              listBooleanParam: null,
              stringParam: null,
              listStringParam: null,
              enumParam: null,
              listEnumParam: null,
            }) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {
                "data": {
                    "objectField": "SUCCESS-"
                    "[intParam:None]-"
                    "[listIntParam:None]-"
                    "[floatParam:None]-"
                    "[listFloatParam:None]-"
                    "[booleanParam:None]-"
                    "[listBooleanParam:None]-"
                    "[stringParam:None]-"
                    "[listStringParam:None]-"
                    "[enumParam:None]-"
                    "[listEnumParam:None]"
                }
            },
        ),
        (
            """
            query ObjectParamWithDefault($value: ObjectInput = {
              intParam: 20,
              listIntParam: [20, 21, null],
              floatParam: 23456.789e2,
              listFloatParam: [23456.789e2, 12.4, -1, 0.2e1, null],
              booleanParam: false,
              listBooleanParam: [false, true, null],
              stringParam: "defaultValue",
              listStringParam: ["firstDefaultValue", "secondDefaultValue", null],
              enumParam: ENUM_2,
              listEnumParam: [ENUM_2, ENUM_3, null],
            }) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {
                "data": {
                    "objectField": "SUCCESS-"
                    "[intParam:22]-"
                    "[listIntParam:20-21-None]-"
                    "[floatParam:2345680.9]-"
                    "[listFloatParam:2345678.9-12.4--1.0-2.0-None]-"
                    "[booleanParam:False]-"
                    "[listBooleanParam:False-True-None]-"
                    "[stringParam:defaultvalue]-"
                    "[listStringParam:firstDefaultValue-secondDefaultValue-None]-"
                    "[enumParam:enum_2]-"
                    "[listEnumParam:ENUM_2-ENUM_3-None]"
                }
            },
        ),
        # NonNullWrapperObjectInput
        (
            """
            query ObjectParamWithDefault($value: NonNullWrapperObjectInput = {
              intParam: null,
              listIntParam: null,
              floatParam: null,
              listFloatParam: null,
              booleanParam: null,
              listBooleanParam: null,
              stringParam: null,
              listStringParam: null,
              enumParam: null,
              listEnumParam: null,
            }) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {"data": {"objectField": "SUCCESS"}},
        ),
        (
            """
            query ObjectParamWithDefault($value: NonNullWrapperObjectInput = {
              intParam: 20,
              listIntParam: [20, 21, null],
              floatParam: 23456.789e2,
              listFloatParam: [23456.789e2, 12.4, -1, 0.2e1, null],
              booleanParam: false,
              listBooleanParam: [false, true, null],
              stringParam: "defaultValue",
              listStringParam: ["firstDefaultValue", "secondDefaultValue", null],
              enumParam: ENUM_2,
              listEnumParam: [ENUM_2, ENUM_3, null],
            }) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {
                "data": {
                    "objectField": "SUCCESS-"
                    "[intParam:20]-"
                    "[listIntParam:20-21-None]-"
                    "[floatParam:2345678.9]-"
                    "[listFloatParam:2345678.9-12.4--1.0-2.0-None]-"
                    "[booleanParam:False]-"
                    "[listBooleanParam:False-True-None]-"
                    "[stringParam:defaultValue]-"
                    "[listStringParam:firstDefaultValue-secondDefaultValue-None]-"
                    "[enumParam:ENUM_2]-"
                    "[listEnumParam:ENUM_2-ENUM_3-None]"
                }
            },
        ),
        # NonNullInnerObjectInput
        (
            """
            query ObjectParamWithDefault($value: NonNullInnerObjectInput = {
              intParam: null,
              listIntParam: null,
              floatParam: null,
              listFloatParam: null,
              booleanParam: null,
              listBooleanParam: null,
              stringParam: null,
              listStringParam: null,
              enumParam: null,
              listEnumParam: null,
            }) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {
                "data": {
                    "objectField": "SUCCESS-"
                    "[intParam:None]-"
                    "[listIntParam:None]-"
                    "[floatParam:None]-"
                    "[listFloatParam:None]-"
                    "[booleanParam:None]-"
                    "[listBooleanParam:None]-"
                    "[stringParam:None]-"
                    "[listStringParam:None]-"
                    "[enumParam:None]-"
                    "[listEnumParam:None]"
                }
            },
        ),
        (
            """
            query ObjectParamWithDefault($value: NonNullInnerObjectInput = {
              intParam: 20,
              listIntParam: [20, 21, null],
              floatParam: 23456.789e2,
              listFloatParam: [23456.789e2, 12.4, -1, 0.2e1, null],
              booleanParam: false,
              listBooleanParam: [false, true, null],
              stringParam: "defaultValue",
              listStringParam: ["firstDefaultValue", "secondDefaultValue", null],
              enumParam: ENUM_2,
              listEnumParam: [ENUM_2, ENUM_3, null],
            }) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {"data": {"objectField": "SUCCESS"}},
        ),
        (
            """
            query ObjectParamWithDefault($value: NonNullInnerObjectInput = {
              intParam: 20,
              listIntParam: [20, 21],
              floatParam: 23456.789e2,
              listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
              booleanParam: false,
              listBooleanParam: [false, true],
              stringParam: "defaultValue",
              listStringParam: ["firstDefaultValue", "secondDefaultValue"],
              enumParam: ENUM_2,
              listEnumParam: [ENUM_2, ENUM_3],
            }) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {
                "data": {
                    "objectField": "SUCCESS-"
                    "[intParam:20]-"
                    "[listIntParam:20-21]-"
                    "[floatParam:2345678.9]-"
                    "[listFloatParam:2345678.9-12.4--1.0-2.0]-"
                    "[booleanParam:False]-"
                    "[listBooleanParam:False-True]-"
                    "[stringParam:defaultValue]-"
                    "[listStringParam:firstDefaultValue-secondDefaultValue]-"
                    "[enumParam:ENUM_2]-"
                    "[listEnumParam:ENUM_2-ENUM_3]"
                }
            },
        ),
        # ObjectInputWithDefault
        (
            """
            query ObjectParam($value: ObjectInputWithDefault = null) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {"data": {"objectField": "SUCCESS-None"}},
        ),
        (
            """
            query ObjectParam($value: ObjectInputWithDefault) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {"data": {"objectField": "SUCCESS"}},  # TODO: normal?
        ),
        (
            """
            query ObjectParam($value: ObjectInputWithDefault = {}) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {
                "data": {
                    "objectField": "SUCCESS-"
                    "[intParam:10]-"
                    "[listIntParam:20-21]-"
                    "[listFloatParam:2345678.9-12.4--1-2.0]-"
                    "[booleanParam:False]-"
                    "[listBooleanParam:False-True]-"
                    "[stringParam:defaultValue]-"
                    "[listStringParam:firstDefaultValue-secondDefaultValue]-"
                    "[enumParam:ENUM_2]-"
                    "[listEnumParam:ENUM_2-ENUM_3]"
                }
            },
        ),
        (
            """
            query ObjectParamWithDefault($value: ObjectInputWithDefault = {
              intParam: null,
              listIntParam: null,
              floatParam: null,
              listFloatParam: null,
              booleanParam: null,
              listBooleanParam: null,
              stringParam: null,
              listStringParam: null,
              enumParam: null,
              listEnumParam: null,
            }) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {
                "data": {
                    "objectField": "SUCCESS-"
                    "[intParam:None]-"
                    "[listIntParam:None]-"
                    "[floatParam:None]-"
                    "[listFloatParam:None]-"
                    "[booleanParam:None]-"
                    "[listBooleanParam:None]-"
                    "[stringParam:None]-"
                    "[listStringParam:None]-"
                    "[enumParam:None]-"
                    "[listEnumParam:None]"
                }
            },
        ),
        (
            """
            query ObjectParamWithDefault($value: ObjectInputWithDefault = {
              intParam: 20,
              listIntParam: [20, 21, null],
              floatParam: 23456.789e2,
              listFloatParam: [23456.789e2, 12.4, -1, 0.2e1, null],
              booleanParam: false,
              listBooleanParam: [false, true, null],
              stringParam: "defaultValue",
              listStringParam: ["firstDefaultValue", "secondDefaultValue", null],
              enumParam: ENUM_2,
              listEnumParam: [ENUM_2, ENUM_3, null],
            }) {
              objectField(objectParam: $value)
            }
            """,
            None,
            {
                "data": {
                    "objectField": "SUCCESS-"
                    "[intParam:20]-"
                    "[listIntParam:20-21-None]-"
                    "[floatParam:2345678.9]-"
                    "[listFloatParam:2345678.9-12.4--1.0-2.0-None]-"
                    "[booleanParam:False]-"
                    "[listBooleanParam:False-True-None]-"
                    "[stringParam:defaultValue]-"
                    "[listStringParam:firstDefaultValue-secondDefaultValue-None]-"
                    "[enumParam:ENUM_2]-"
                    "[listEnumParam:ENUM_2-ENUM_3-None]"
                }
            },
        ),
    ],
)
async def test_refactoring_literal_directives_object(
    ttftt_engine, query, variables, expected
):
    assert await ttftt_engine.execute(query, variables=variables) == expected


# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "query,variables,expected",
#     [
#         # ObjectParam not dict
#         (
#             """
#             query ObjectParam($value: ObjectInput) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {"value": "isn't an object"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 31, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "isn't an object >; Expected type < "
#                         "ObjectInput > to be an object.",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         # ObjectParam
#         (
#             """
#             query ObjectParam($value: ObjectInput) {
#               objectField(objectParam: $value)
#             }
#             """,
#             None,
#             {"data": {"objectField": "SUCCESS"}},
#         ),
#         (
#             """
#             query ObjectParam($value: ObjectInput) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {"value": None},
#             {"data": {"objectField": "SUCCESS-None"}},
#         ),
#         (
#             """
#             query ObjectParam($value: ObjectInput) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {
#                 "value": {
#                     "intParam": 10,
#                     "listIntParam": [None, 10],
#                     "floatParam": 123_456.789e2,
#                     "listFloatParam": [None, 123_456.789e2, 23.5, -2, 0.3e1],
#                     "booleanParam": True,
#                     "listBooleanParam": [None, True, False],
#                     "stringParam": "aValue",
#                     "listStringParam": [None, "firstValue", "secondValue"],
#                     "enumParam": "ENUM_1",
#                     "listEnumParam": [None, "ENUM_1", "ENUM_2"],
#                 }
#             },
#             {
#                 "data": {
#                     "objectField": "SUCCESS-"
#                     "[intParam:12]-"
#                     "[listIntParam:None-10]-"
#                     "[floatParam:12345680.9]-"
#                     "[listFloatParam:None-12345678.9-23.5--2.0-3.0]-"
#                     "[booleanParam:True]-"
#                     "[listBooleanParam:None-True-False]-"
#                     "[stringParam:avalue]-"
#                     "[listStringParam:None-firstValue-secondValue]-"
#                     "[enumParam:enum_1_1]-"
#                     "[listEnumParam:None-enum_1_1-ENUM_2_2]"
#                 }
#             },
#         ),
#         (
#             """
#             query ObjectParam($value: ObjectInput) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {
#                 "value": {
#                     "intParam": 10,
#                     "listIntParam": [10],
#                     "floatParam": 123_456.789e2,
#                     "listFloatParam": [123_456.789e2, 23.5, -2, 0.3e1],
#                     "booleanParam": True,
#                     "listBooleanParam": [True, False],
#                     "stringParam": "aValue",
#                     "listStringParam": ["firstValue", "secondValue"],
#                     "enumParam": "ENUM_1",
#                     "listEnumParam": ["ENUM_1", "ENUM_2"],
#                 }
#             },
#             {
#                 "data": {
#                     "objectField": "SUCCESS-"
#                     "[intParam:12]-"
#                     "[listIntParam:10]-"
#                     "[floatParam:12345680.9]-"
#                     "[listFloatParam:12345678.9-23.5--2.0-3.0]-"
#                     "[booleanParam:True]-"
#                     "[listBooleanParam:True-False]-"
#                     "[stringParam:avalue]-"
#                     "[listStringParam:firstValue-secondValue]-"
#                     "[enumParam:enum_1_1]-"
#                     "[listEnumParam:enum_1_1-ENUM_2_2]"
#                 }
#             },
#         ),
#         # ObjectParamWithDefault
#         (
#             """
#             query ObjectParamWithDefault($value: ObjectInput = {
#               intParam: 20,
#               listIntParam: [20, 21],
#               floatParam: 23456.789e2,
#               listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
#               booleanParam: false,
#               listBooleanParam: [false, true],
#               stringParam: "defaultValue",
#               listStringParam: ["firstDefaultValue", "secondDefaultValue"],
#               enumParam: ENUM_2,
#               listEnumParam: [ENUM_2, ENUM_3],
#             }) {
#               objectField(objectParam: $value)
#             }
#             """,
#             None,
#             {
#                 "data": {
#                     "objectField": "SUCCESS-"
#                     "[intParam:20]-"
#                     "[listIntParam:20-21]-"
#                     "[floatParam:2345678.9]-"
#                     "[listFloatParam:2345678.9-12.4--1.0-2.0]-"
#                     "[booleanParam:False]-"
#                     "[listBooleanParam:False-True]-"
#                     "[stringParam:defaultValue]-"
#                     "[listStringParam:firstDefaultValue-secondDefaultValue]-"
#                     "[enumParam:ENUM_2]-"
#                     "[listEnumParam:ENUM_2-ENUM_3]"
#                 }
#             },
#         ),
#         (
#             """
#             query ObjectParamWithDefault($value: ObjectInput = {
#               intParam: 20,
#               listIntParam: [20, 21],
#               floatParam: 23456.789e2,
#               listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
#               booleanParam: false,
#               listBooleanParam: [false, true],
#               stringParam: "defaultValue",
#               listStringParam: ["firstDefaultValue", "secondDefaultValue"],
#               enumParam: ENUM_2,
#               listEnumParam: [ENUM_2, ENUM_3],
#             }) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {"value": None},
#             {"data": {"objectField": "SUCCESS-None"}},
#         ),
#         (
#             """
#             query ObjectParamWithDefault($value: ObjectInput = {
#               intParam: 20,
#               listIntParam: [20, 21],
#               floatParam: 23456.789e2,
#               listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
#               booleanParam: false,
#               listBooleanParam: [false, true],
#               stringParam: "defaultValue",
#               listStringParam: ["firstDefaultValue", "secondDefaultValue"],
#               enumParam: ENUM_2,
#               listEnumParam: [ENUM_2, ENUM_3],
#             }) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {
#                 "value": {
#                     "intParam": 10,
#                     "listIntParam": [None, 10],
#                     "floatParam": 123_456.789e2,
#                     "listFloatParam": [None, 123_456.789e2, 23.5, -2, 0.3e1],
#                     "booleanParam": True,
#                     "listBooleanParam": [None, True, False],
#                     "stringParam": "aValue",
#                     "listStringParam": [None, "firstValue", "secondValue"],
#                     "enumParam": "ENUM_1",
#                     "listEnumParam": [None, "ENUM_1", "ENUM_2"],
#                 }
#             },
#             {
#                 "data": {
#                     "objectField": "SUCCESS-"
#                     "[intParam:12]-"
#                     "[listIntParam:None-10]-"
#                     "[floatParam:12345680.9]-"
#                     "[listFloatParam:None-12345678.9-23.5--2.0-3.0]-"
#                     "[booleanParam:True]-"
#                     "[listBooleanParam:None-True-False]-"
#                     "[stringParam:avalue]-"
#                     "[listStringParam:None-firstValue-secondValue]-"
#                     "[enumParam:enum_1_1]-"
#                     "[listEnumParam:None-enum_1_1-ENUM_2_2]"
#                 }
#             },
#         ),
#         (
#             """
#             query ObjectParamWithDefault($value: ObjectInput = {
#               intParam: 20,
#               listIntParam: [20, 21],
#               floatParam: 23456.789e2,
#               listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
#               booleanParam: false,
#               listBooleanParam: [false, true],
#               stringParam: "defaultValue",
#               listStringParam: ["firstDefaultValue", "secondDefaultValue"],
#               enumParam: ENUM_2,
#               listEnumParam: [ENUM_2, ENUM_3],
#             }) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {
#                 "value": {
#                     "intParam": 10,
#                     "listIntParam": [10],
#                     "floatParam": 123_456.789e2,
#                     "listFloatParam": [123_456.789e2, 23.5, -2, 0.3e1],
#                     "booleanParam": True,
#                     "listBooleanParam": [True, False],
#                     "stringParam": "aValue",
#                     "listStringParam": ["firstValue", "secondValue"],
#                     "enumParam": "ENUM_1",
#                     "listEnumParam": ["ENUM_1", "ENUM_2"],
#                 }
#             },
#             {
#                 "data": {
#                     "objectField": "SUCCESS-"
#                     "[intParam:12]-"
#                     "[listIntParam:10]-"
#                     "[floatParam:12345680.9]-"
#                     "[listFloatParam:12345678.9-23.5--2.0-3.0]-"
#                     "[booleanParam:True]-"
#                     "[listBooleanParam:True-False]-"
#                     "[stringParam:avalue]-"
#                     "[listStringParam:firstValue-secondValue]-"
#                     "[enumParam:enum_1_1]-"
#                     "[listEnumParam:enum_1_1-ENUM_2_2]"
#                 }
#             },
#         ),
#         # NonNullObjectParam
#         (
#             """
#             query NonNullObjectParam($value: NonNullObjectInput!) {
#               objectField(objectParam: $value)
#             }
#             """,
#             None,
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "message": "Variable < $value > of required type "
#                         "< NonNullObjectInput! > was not provided.",
#                         "path": None,
#                         "locations": [{"line": 2, "column": 38}],
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query NonNullObjectParam($value: NonNullObjectInput!) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {"value": None},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "message": "Variable < $value > of non-null type "
#                         "< NonNullObjectInput! > must not be null.",
#                         "path": None,
#                         "locations": [{"line": 2, "column": 38}],
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query NonNullObjectParam($value: NonNullObjectInput!) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {
#                 "value": {
#                     "intParam": None,
#                     "listIntParam": [None, 10],
#                     "floatParam": None,
#                     "listFloatParam": [None, 123_456.789e2, 23.5, -2, 0.3e1],
#                     "booleanParam": None,
#                     "listBooleanParam": [None, True, False],
#                     "stringParam": None,
#                     "listStringParam": [None, "firstValue", "secondValue"],
#                     "enumParam": None,
#                     "listEnumParam": [None, "ENUM_1", "ENUM_2"],
#                 }
#             },
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], 'floatParam': None, "
#                         "'listFloatParam': [None, 12345678.9, "
#                         "23.5, -2, 3.0], 'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, 'firstValue', 'secondValue'], "
#                         "'enumParam': None, 'listEnumParam': ["
#                         "None, 'ENUM_1', 'ENUM_2']} >; Expected "
#                         "non-nullable type < Int! > not to be "
#                         "null at value.intParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], 'floatParam': None, "
#                         "'listFloatParam': [None, 12345678.9, "
#                         "23.5, -2, 3.0], 'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, 'firstValue', 'secondValue'], "
#                         "'enumParam': None, 'listEnumParam': ["
#                         "None, 'ENUM_1', 'ENUM_2']} >; Expected "
#                         "non-nullable type < Int! > not to be "
#                         "null at value.listIntParam[0].",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], 'floatParam': None, "
#                         "'listFloatParam': [None, 12345678.9, "
#                         "23.5, -2, 3.0], 'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, 'firstValue', 'secondValue'], "
#                         "'enumParam': None, 'listEnumParam': ["
#                         "None, 'ENUM_1', 'ENUM_2']} >; Expected "
#                         "non-nullable type < Float! > not to be "
#                         "null at value.floatParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], 'floatParam': None, "
#                         "'listFloatParam': [None, 12345678.9, "
#                         "23.5, -2, 3.0], 'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, 'firstValue', 'secondValue'], "
#                         "'enumParam': None, 'listEnumParam': ["
#                         "None, 'ENUM_1', 'ENUM_2']} >; Expected "
#                         "non-nullable type < Float! > not to be "
#                         "null at value.listFloatParam[0].",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], 'floatParam': None, "
#                         "'listFloatParam': [None, 12345678.9, "
#                         "23.5, -2, 3.0], 'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, 'firstValue', 'secondValue'], "
#                         "'enumParam': None, 'listEnumParam': ["
#                         "None, 'ENUM_1', 'ENUM_2']} >; Expected "
#                         "non-nullable type < Boolean! > not to be "
#                         "null at value.booleanParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], 'floatParam': None, "
#                         "'listFloatParam': [None, 12345678.9, "
#                         "23.5, -2, 3.0], 'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, 'firstValue', 'secondValue'], "
#                         "'enumParam': None, 'listEnumParam': ["
#                         "None, 'ENUM_1', 'ENUM_2']} >; Expected "
#                         "non-nullable type < Boolean! > not to be "
#                         "null at value.listBooleanParam[0].",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < String! > "
#                         "not to be "
#                         "null at value.stringParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < String! > "
#                         "not to be "
#                         "null at value.listStringParam[0].",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < MyEnum! > "
#                         "not to be "
#                         "null at value.enumParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 38, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < MyEnum! > "
#                         "not to be "
#                         "null at value.listEnumParam[0].",
#                         "path": None,
#                     },
#                 ],
#             },
#         ),
#         (
#             """
#             query NonNullObjectParam($value: NonNullObjectInput!) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {
#                 "value": {
#                     "intParam": 10,
#                     "listIntParam": [10],
#                     "floatParam": 123_456.789e2,
#                     "listFloatParam": [123_456.789e2, 23.5, -2, 0.3e1],
#                     "booleanParam": True,
#                     "listBooleanParam": [True, False],
#                     "stringParam": "aValue",
#                     "listStringParam": ["firstValue", "secondValue"],
#                     "enumParam": "ENUM_1",
#                     "listEnumParam": ["ENUM_1", "ENUM_2"],
#                 }
#             },
#             {
#                 "data": {
#                     "objectField": "SUCCESS-"
#                     "[intParam:10]-"
#                     "[listIntParam:10]-"
#                     "[floatParam:12345678.9]-"
#                     "[listFloatParam:12345678.9-23.5--2.0-3.0]-"
#                     "[booleanParam:True]-"
#                     "[listBooleanParam:True-False]-"
#                     "[stringParam:aValue]-"
#                     "[listStringParam:firstValue-secondValue]-"
#                     "[enumParam:enum_1_1]-"
#                     "[listEnumParam:enum_1_1-ENUM_2_2]"
#                 }
#             },
#         ),
#         # NonNullObjectParamWithDefault
#         (
#             """
#             query NonNullObjectParamWithDefault($value: NonNullObjectInput! = {
#               intParam: 20,
#               listIntParam: [20, 21],
#               floatParam: 23456.789e2,
#               listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
#               booleanParam: false,
#               listBooleanParam: [false, true],
#               stringParam: "defaultValue",
#               listStringParam: ["firstDefaultValue", "secondDefaultValue"],
#               enumParam: ENUM_2,
#               listEnumParam: [ENUM_2, ENUM_3],
#             }) {
#               objectField(objectParam: $value)
#             }
#             """,
#             None,
#             {
#                 "data": {
#                     "objectField": "SUCCESS-"
#                     "[intParam:20]-"
#                     "[listIntParam:20-21]-"
#                     "[floatParam:2345678.9]-"
#                     "[listFloatParam:2345678.9-12.4--1.0-2.0]-"
#                     "[booleanParam:False]-"
#                     "[listBooleanParam:False-True]-"
#                     "[stringParam:defaultValue]-"
#                     "[listStringParam:firstDefaultValue-secondDefaultValue]-"
#                     "[enumParam:ENUM_2]-"
#                     "[listEnumParam:ENUM_2-ENUM_3]"
#                 }
#             },
#         ),
#         (
#             """
#             query NonNullObjectParamWithDefault($value: NonNullObjectInput! = {
#               intParam: 20,
#               listIntParam: [20, 21],
#               floatParam: 23456.789e2,
#               listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
#               booleanParam: false,
#               listBooleanParam: [false, true],
#               stringParam: "defaultValue",
#               listStringParam: ["firstDefaultValue", "secondDefaultValue"],
#               enumParam: ENUM_2,
#               listEnumParam: [ENUM_2, ENUM_3],
#             }) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {"value": None},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "message": "Variable < $value > of non-null type "
#                         "< NonNullObjectInput! > must not be null.",
#                         "path": None,
#                         "locations": [{"line": 2, "column": 49}],
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query NonNullObjectParamWithDefault($value: NonNullObjectInput! = {
#               intParam: 20,
#               listIntParam: [20, 21],
#               floatParam: 23456.789e2,
#               listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
#               booleanParam: false,
#               listBooleanParam: [false, true],
#               stringParam: "defaultValue",
#               listStringParam: ["firstDefaultValue", "secondDefaultValue"],
#               enumParam: ENUM_2,
#               listEnumParam: [ENUM_2, ENUM_3],
#             }) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {
#                 "value": {
#                     "intParam": None,
#                     "listIntParam": [None, 10],
#                     "floatParam": None,
#                     "listFloatParam": [None, 123_456.789e2, 23.5, -2, 0.3e1],
#                     "booleanParam": None,
#                     "listBooleanParam": [None, True, False],
#                     "stringParam": None,
#                     "listStringParam": [None, "firstValue", "secondValue"],
#                     "enumParam": None,
#                     "listEnumParam": [None, "ENUM_1", "ENUM_2"],
#                 }
#             },
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < Int! > not "
#                         "to be null "
#                         "at value.intParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < Int! > not "
#                         "to be null "
#                         "at value.listIntParam[0].",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < Float! > "
#                         "not to be "
#                         "null at value.floatParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < Float! > "
#                         "not to be "
#                         "null at value.listFloatParam[0].",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < Boolean! > "
#                         "not to be "
#                         "null at value.booleanParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < Boolean! > "
#                         "not to be "
#                         "null at value.listBooleanParam[0].",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < String! > "
#                         "not to be "
#                         "null at value.stringParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < String! > "
#                         "not to be "
#                         "null at value.listStringParam[0].",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < MyEnum! > "
#                         "not to be "
#                         "null at value.enumParam.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'intParam': None, 'listIntParam': ["
#                         "None, 10], "
#                         "'floatParam': None, 'listFloatParam': ["
#                         "None, "
#                         "12345678.9, 23.5, -2, 3.0], "
#                         "'booleanParam': None, "
#                         "'listBooleanParam': [None, True, False], "
#                         "'stringParam': None, 'listStringParam': "
#                         "[None, "
#                         "'firstValue', 'secondValue'], "
#                         "'enumParam': None, "
#                         "'listEnumParam': [None, 'ENUM_1', "
#                         "'ENUM_2']} >; "
#                         "Expected non-nullable type < MyEnum! > "
#                         "not to be "
#                         "null at value.listEnumParam[0].",
#                         "path": None,
#                     },
#                 ],
#             },
#         ),
#         (
#             """
#             query NonNullObjectParamWithDefault($value: NonNullObjectInput! = {
#               intParam: 20,
#               listIntParam: [20, 21],
#               floatParam: 23456.789e2,
#               listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
#               booleanParam: false,
#               listBooleanParam: [false, true],
#               stringParam: "defaultValue",
#               listStringParam: ["firstDefaultValue", "secondDefaultValue"],
#               enumParam: ENUM_2,
#               listEnumParam: [ENUM_2, ENUM_3],
#             }) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {
#                 "value": {
#                     "intParam": 10,
#                     "listIntParam": [10],
#                     "floatParam": 123_456.789e2,
#                     "listFloatParam": [123_456.789e2, 23.5, -2, 0.3e1],
#                     "booleanParam": True,
#                     "listBooleanParam": [True, False],
#                     "stringParam": "aValue",
#                     "listStringParam": ["firstValue", "secondValue"],
#                     "enumParam": "ENUM_1",
#                     "listEnumParam": ["ENUM_1", "ENUM_2"],
#                 }
#             },
#             {
#                 "data": {
#                     "objectField": "SUCCESS-"
#                     "[intParam:10]-"
#                     "[listIntParam:10]-"
#                     "[floatParam:12345678.9]-"
#                     "[listFloatParam:12345678.9-23.5--2.0-3.0]-"
#                     "[booleanParam:True]-"
#                     "[listBooleanParam:True-False]-"
#                     "[stringParam:aValue]-"
#                     "[listStringParam:firstValue-secondValue]-"
#                     "[enumParam:enum_1_1]-"
#                     "[listEnumParam:enum_1_1-ENUM_2_2]"
#                 }
#             },
#         ),
#         # NonNullObjectParam value not provided
#         (
#             """
#             query NonNullObjectParamWithDefault($value: NonNullObjectInput!) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {"value": {}},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.intParam > of "
#                         "required type < "
#                         "Int! > was not provided.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.listIntParam > of "
#                         "required type "
#                         "< [Int!]! > was not provided.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.floatParam > of "
#                         "required type < "
#                         "Float! > was not provided.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.listFloatParam > of "
#                         "required "
#                         "type < [Float!]! > was not provided.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.booleanParam > of "
#                         "required type "
#                         "< Boolean! > was not provided.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.listBooleanParam > "
#                         "of required "
#                         "type < [Boolean!]! > was not provided.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.stringParam > of "
#                         "required type "
#                         "< String! > was not provided.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.listStringParam > of "
#                         "required "
#                         "type < [String!]! > was not provided.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.enumParam > of "
#                         "required type < "
#                         "MyEnum! > was not provided.",
#                         "path": None,
#                     },
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{} >; Field < value.listEnumParam > of "
#                         "required "
#                         "type < [MyEnum!]! > was not provided.",
#                         "path": None,
#                     },
#                 ],
#             },
#         ),
#         # ObjectParam field not defined
#         (
#             """
#             query NonNullObjectParamWithDefault($value: ObjectInput = {
#               intParam: 20,
#               listIntParam: [20, 21],
#               floatParam: 23456.789e2,
#               listFloatParam: [23456.789e2, 12.4, -1, 0.2e1],
#               booleanParam: false,
#               listBooleanParam: [false, true],
#               stringParam: "defaultValue",
#               listStringParam: ["firstDefaultValue", "secondDefaultValue"],
#               enumParam: ENUM_2,
#               listEnumParam: [ENUM_2, ENUM_3],
#             }) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {"value": {"unknownField": True}},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 49, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'unknownField': True} >; Field < "
#                         "unknownField > is "
#                         "not defined by type < ObjectInput >..",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#     ],
# )
# async def test_refactoring_literal_directives_object(
#     ttftt_engine, query, variables, expected
# ):
#     assert await ttftt_engine.execute(query, variables=variables) == expected
#
#
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "query,variables,expected",
#     [
#         (
#             """
#             query EnumParam($value: MyEnum) {
#               enumField(enumParam: $value)
#             }
#             """,
#             {"value": "UNKNOWN"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 29, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "UNKNOWN >; Expected type < MyEnum >.",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query ListEnumParam($values: [MyEnum]) {
#               listEnumField(listEnumParam: $values)
#             }
#             """,
#             {"values": [None, "ENUM_1", "UNKNOWN"]},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 33, "line": 2}],
#                         "message": "Variable < $values > got invalid value < "
#                         "[None, 'ENUM_1', 'UNKNOWN'] >; Expected "
#                         "type < "
#                         "MyEnum > at value[2].",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#     ],
# )
# async def test_refactoring_literal_directives_unknown_enum(
#     ttftt_engine, query, variables, expected
# ):
#     assert await ttftt_engine.execute(query, variables=variables) == expected
#
#
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "query,variables,expected",
#     [
#         # IntParam
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": 10},
#             {"data": {"intField": "SUCCESS-10"}},
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": 0.0},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "0.0 >; Expected type < Int >; Int cannot represent "
#                         "non-integer value: < 0.0 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": 2_147_483_647},
#             {"data": {"intField": "SUCCESS-2147483647"}},
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": -2_147_483_648},
#             {"data": {"intField": "SUCCESS--2147483648"}},
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": 2_147_483_648},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "2147483648 >; Expected type < Int >; Int cannot "
#                         "represent non 32-bit signed integer value: < "
#                         "2147483648 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": -2_147_483_649},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "-2147483649 >; Expected type < Int >; Int cannot "
#                         "represent non 32-bit signed integer value: < "
#                         "-2147483649 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": "10"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "10 >; Expected type < Int >; Int cannot represent "
#                         "non-integer value: < 10 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": True},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "True >; Expected type < Int >; Int cannot represent "
#                         "non-integer value: < True >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": False},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "False >; Expected type < Int >; Int cannot "
#                         "represent non-integer value: < False >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": 10.23},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "10.23 >; Expected type < Int >; Int cannot "
#                         "represent non-integer value: < 10.23 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": 123_456.789e2},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "12345678.9 >; Expected type < Int >; Int cannot "
#                         "represent non-integer value: < 12345678.9 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": "10.23"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "10.23 >; Expected type < Int >; Int cannot "
#                         "represent non-integer value: < 10.23 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": "123_456.789e2"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "123_456.789e2 >; Expected type < Int >; Int cannot "
#                         "represent non-integer value: < 123_456.789e2 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": "not_an_int"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "not_an_int >; Expected type < Int >; Int cannot "
#                         "represent non-integer value: < not_an_int >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query IntParam($value: Int) {
#               intField(intParam: $value)
#             }
#             """,
#             {"value": {"invalid": "type"}},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 28, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'invalid': 'type'} >; Expected type < Int >; Int "
#                         "cannot represent non-integer value: < {'invalid': "
#                         "'type'} >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         # FloatParam
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": 10},
#             {"data": {"floatField": "SUCCESS-10.0"}},
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": 0.0},
#             {"data": {"floatField": "SUCCESS-0.0"}},
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": 2_147_483_647},
#             {"data": {"floatField": "SUCCESS-2147483647.0"}},
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": 2_147_483_646.9},
#             {"data": {"floatField": "SUCCESS-2147483646.9"}},
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": -2_147_483_648},
#             {"data": {"floatField": "SUCCESS--2147483648.0"}},
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": -2_147_483_647.9},
#             {"data": {"floatField": "SUCCESS--2147483647.9"}},
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": 2_147_483_648},
#             {"data": {"floatField": "SUCCESS-2147483648.0"}},
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": -2_147_483_649},
#             {"data": {"floatField": "SUCCESS--2147483649.0"}},
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": 123_456.789e2},
#             {"data": {"floatField": "SUCCESS-12345678.9"}},
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": "123_456.789e2"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 30, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "123_456.789e2 >; Expected type < Float >; Float "
#                         "cannot represent non numeric value: < 123_456.789e2 "
#                         ">",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": True},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 30, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "True >; Expected type < Float >; Float cannot "
#                         "represent non numeric value: < True >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": False},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 30, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "False >; Expected type < Float >; Float cannot "
#                         "represent non numeric value: < False >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": "not_a_float"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 30, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "not_a_float >; Expected type < Float >; Float "
#                         "cannot represent non numeric value: < not_a_float >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query FloatParam($value: Float) {
#               floatField(floatParam: $value)
#             }
#             """,
#             {"value": {"invalid": "type"}},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 30, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'invalid': 'type'} >; Expected type < Float >; "
#                         "Float cannot represent non numeric value: < {"
#                         "'invalid': 'type'} >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         # BooleanParam
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": True},
#             {"data": {"booleanField": "SUCCESS-True"}},
#         ),
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": False},
#             {"data": {"booleanField": "SUCCESS-False"}},
#         ),
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": "True"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 32, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "True >; Expected type < Boolean >; Boolean cannot "
#                         "represent a non boolean value: < True >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": "False"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 32, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "False >; Expected type < Boolean >; Boolean cannot "
#                         "represent a non boolean value: < False >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": "true"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 32, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "true >; Expected type < Boolean >; Boolean cannot "
#                         "represent a non boolean value: < true >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": "false"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 32, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "false >; Expected type < Boolean >; Boolean cannot "
#                         "represent a non boolean value: < false >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": 1},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 32, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "1 >; Expected type < Boolean >; Boolean cannot "
#                         "represent a non boolean value: < 1 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": 0},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 32, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "0 >; Expected type < Boolean >; Boolean cannot "
#                         "represent a non boolean value: < 0 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": "1"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 32, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "1 >; Expected type < Boolean >; Boolean cannot "
#                         "represent a non boolean value: < 1 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query BooleanParam($value: Boolean) {
#               booleanField(booleanParam: $value)
#             }
#             """,
#             {"value": "0"},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 32, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "0 >; Expected type < Boolean >; Boolean cannot "
#                         "represent a non boolean value: < 0 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         # StringParam
#         (
#             """
#             query StringParam($value: String) {
#               stringField(stringParam: $value)
#             }
#             """,
#             {"value": "aValue"},
#             {"data": {"stringField": "SUCCESS-aValue"}},
#         ),
#         (
#             """
#             query StringParam($value: String) {
#               stringField(stringParam: $value)
#             }
#             """,
#             {"value": 10},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 31, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "10 >; Expected type < String >; String cannot "
#                         "represent a non string value: < 10 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query StringParam($value: String) {
#               stringField(stringParam: $value)
#             }
#             """,
#             {"value": 10.2},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 31, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "10.2 >; Expected type < String >; String cannot "
#                         "represent a non string value: < 10.2 >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query StringParam($value: String) {
#               stringField(stringParam: $value)
#             }
#             """,
#             {"value": True},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 31, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "True >; Expected type < String >; String cannot "
#                         "represent a non string value: < True >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#         (
#             """
#             query StringParam($value: String) {
#               stringField(stringParam: $value)
#             }
#             """,
#             {"value": {"invalid": "type"}},
#             {
#                 "data": None,
#                 "errors": [
#                     {
#                         "locations": [{"column": 31, "line": 2}],
#                         "message": "Variable < $value > got invalid value < "
#                         "{'invalid': 'type'} >; Expected type < String >; "
#                         "String cannot represent a non string value: < {"
#                         "'invalid': 'type'} >",
#                         "path": None,
#                     }
#                 ],
#             },
#         ),
#     ],
# )
# async def test_refactoring_literal_directives_scalar_coerce(
#     ttftt_engine, query, variables, expected
# ):
#     assert await ttftt_engine.execute(query, variables=variables) == expected
#
#
# @pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "query,variables,expected",
#     [
#         (
#             """
#             query ObjectParam($value: ObjectInputWithDefault) {
#               objectField(objectParam: $value)
#             }
#             """,
#             {"value": {}},
#             # TODO: this isn't the real expected value. Investigate on it.
#             {
#                 "data": {
#                     "objectField": "SUCCESS-[intParam:10]-[listIntParam:20-21]-[listFloatParam:2345678.9-12.4--1-2.0]-[booleanParam:False]-[listBooleanParam:False-True]-[stringParam:defaultValue]-[listStringParam:firstDefaultValue-secondDefaultValue]-[enumParam:ENUM_2]-[listEnumParam:ENUM_2-ENUM_3]"
#                 }
#             },
#         )
#     ],
# )
# async def test_refactoring_literal_directives_object_with_schema_default_value(
#     ttftt_engine, query, variables, expected
# ):
#     assert await ttftt_engine.execute(query, variables=variables) == expected
