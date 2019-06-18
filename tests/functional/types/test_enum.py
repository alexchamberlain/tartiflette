import pytest

from tartiflette import Resolver, create_engine


@pytest.mark.asyncio
async def test_tartiflette_execute_enum_type_output(clean_registry):
    schema_sdl = """
    enum Test {
        Value1
        Value2
        Value3
    }

    type Query {
        enumTest: Test
    }
    """

    @Resolver("Query.enumTest")
    async def func_field_resolver(*args, **kwargs):
        return "Value1"

    ttftt = await create_engine(schema_sdl)

    result = await ttftt.execute(
        """
    query Test{
        enumTest
    }
    """,
        operation_name="Test",
    )

    assert {"data": {"enumTest": "Value1"}} == result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_sdl,resolver_response,expected",
    [
        ("Test", "Value1", {"data": {"testField": "Value1"}}),
        (
            "Test!",
            None,
            {
                "data": None,
                "errors": [
                    {
                        "message": "Cannot return null for non-nullable field Query.testField.",
                        "path": ["testField"],
                        "locations": [{"line": 3, "column": 9}],
                    }
                ],
            },
        ),
        (
            "[Test]",
            ["Value3", "Value1"],
            {"data": {"testField": ["Value3", "Value1"]}},
        ),
        (
            "[Test]",
            ["Value3", "UnknownValue"],
            {
                "data": {
                    "testField": ["Value3", None]
                },  # TODO: should check this, I'm not sure that the expected behavior
                "errors": [
                    {
                        "message": "Expected value of type Test but received <class 'str'>.",
                        "path": ["testField", 1],
                        "locations": [{"line": 3, "column": 9}],
                    }
                ],
            },
        ),
        (
            "[Test!]",
            ["Value3", "UnknownValue"],
            {
                "data": {"testField": None},
                "errors": [
                    {
                        "message": "Expected value of type Test but received <class 'str'>.",
                        "path": ["testField", 1],
                        "locations": [{"line": 3, "column": 9}],
                    }
                ],
            },
        ),
        (
            "[Test!]!",
            ["Value3", "UnknownValue"],
            {
                "data": None,
                "errors": [
                    {
                        "message": "Expected value of type Test but received <class 'str'>.",
                        "path": ["testField", 1],
                        "locations": [{"line": 3, "column": 9}],
                    }
                ],
            },
        ),
    ],
)
async def test_tartiflette_execute_enum_type_advanced(
    input_sdl, resolver_response, expected, clean_registry
):
    schema_sdl = """
    enum Test {{
        Value1
        Value2
        Value3
    }}

    type Query {{
        testField: {}
    }}
    """.format(
        input_sdl
    )

    @Resolver("Query.testField")
    async def func_field_resolver(*args, **kwargs):
        return resolver_response

    ttftt = await create_engine(schema_sdl)

    result = await ttftt.execute(
        """
    query Test{
        testField
    }
    """,
        operation_name="Test",
    )

    assert expected == result
