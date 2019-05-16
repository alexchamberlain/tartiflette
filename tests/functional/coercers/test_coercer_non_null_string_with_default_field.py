import pytest

from tests.functional.coercers.common import resolve_unwrapped_field


@pytest.mark.asyncio
@pytest.mark.ttftt_engine(
    name="coercion",
    resolvers={"Query.nonNullStringWithDefaultField": resolve_unwrapped_field},
)
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        (
            """query { nonNullStringWithDefaultField }""",
            None,
            {
                "data": {
                    # TODO: following value is the "real" expected value
                    # default value from schema object aren't properly handled and aren't coerced
                    # when fixed, don't forget to replace the expected value for this test case
                    # "nonNullStringWithDefaultField": "SUCCESS-defaultstring-scalar-nonNullStringWithDefaultField"
                    "nonNullStringWithDefaultField": "SUCCESS-defaultString-nonNullStringWithDefaultField"
                }
            },
        ),
        (
            """query { nonNullStringWithDefaultField(param: null) }""",
            None,
            {
                "data": {"nonNullStringWithDefaultField": None},
                "errors": [
                    {
                        "message": "Argument < param > of non-null type < String! > must not be null.",
                        "path": ["nonNullStringWithDefaultField"],
                        "locations": [{"line": 1, "column": 46}],
                    }
                ],
            },
        ),
        (
            """query { nonNullStringWithDefaultField(param: "paramDefaultValue") }""",
            None,
            {
                "data": {
                    "nonNullStringWithDefaultField": "SUCCESS-paramdefaultvalue-scalar-nonNullStringWithDefaultField"
                }
            },
        ),
        (
            """query ($param: String) { nonNullStringWithDefaultField(param: $param) }""",
            None,
            {
                "data": {
                    # TODO: following value is the "real" expected value
                    # default value from schema object aren't properly handled and aren't coerced
                    # when fixed, don't forget to replace the expected value for this test case
                    # "nonNullStringWithDefaultField": "SUCCESS-defaultstring-scalar-nonNullStringWithDefaultField"
                    "nonNullStringWithDefaultField": "SUCCESS-defaultString-nonNullStringWithDefaultField"
                }
            },
        ),
        (
            """query ($param: String) { nonNullStringWithDefaultField(param: $param) }""",
            {"param": None},
            {
                "data": {"nonNullStringWithDefaultField": None},
                "errors": [
                    {
                        "message": "Argument < param > of non-null type < String! > must not be null.",
                        "path": ["nonNullStringWithDefaultField"],
                        "locations": [{"line": 1, "column": 63}],
                    }
                ],
            },
        ),
        (
            """query ($param: String) { nonNullStringWithDefaultField(param: $param) }""",
            {"param": "varValue"},
            {
                "data": {
                    "nonNullStringWithDefaultField": "SUCCESS-varvalue-scalar-nonNullStringWithDefaultField"
                }
            },
        ),
        (
            """query ($param: String = null) { nonNullStringWithDefaultField(param: $param) }""",
            None,
            {
                "data": {"nonNullStringWithDefaultField": None},
                "errors": [
                    {
                        "message": "Argument < param > of non-null type < String! > must not be null.",
                        "path": ["nonNullStringWithDefaultField"],
                        "locations": [{"line": 1, "column": 70}],
                    }
                ],
            },
        ),
        (
            """query ($param: String = null) { nonNullStringWithDefaultField(param: $param) }""",
            {"param": None},
            {
                "data": {"nonNullStringWithDefaultField": None},
                "errors": [
                    {
                        "message": "Argument < param > of non-null type < String! > must not be null.",
                        "path": ["nonNullStringWithDefaultField"],
                        "locations": [{"line": 1, "column": 70}],
                    }
                ],
            },
        ),
        (
            """query ($param: String = null) { nonNullStringWithDefaultField(param: $param) }""",
            {"param": "varValue"},
            {
                "data": {
                    "nonNullStringWithDefaultField": "SUCCESS-varvalue-scalar-nonNullStringWithDefaultField"
                }
            },
        ),
        (
            """query ($param: String = "varDefault") { nonNullStringWithDefaultField(param: $param) }""",
            None,
            {
                "data": {
                    "nonNullStringWithDefaultField": "SUCCESS-vardefault-scalar-nonNullStringWithDefaultField"
                }
            },
        ),
        (
            """query ($param: String = "varDefault") { nonNullStringWithDefaultField(param: $param) }""",
            {"param": None},
            {
                "data": {"nonNullStringWithDefaultField": None},
                "errors": [
                    {
                        "message": "Argument < param > of non-null type < String! > must not be null.",
                        "path": ["nonNullStringWithDefaultField"],
                        "locations": [{"line": 1, "column": 78}],
                    }
                ],
            },
        ),
        (
            """query ($param: String = "varDefault") { nonNullStringWithDefaultField(param: $param) }""",
            {"param": "varValue"},
            {
                "data": {
                    "nonNullStringWithDefaultField": "SUCCESS-varvalue-scalar-nonNullStringWithDefaultField"
                }
            },
        ),
        (
            """query ($param: String!) { nonNullStringWithDefaultField(param: $param) }""",
            None,
            {
                "data": None,
                "errors": [
                    {
                        "message": "Variable < $param > of required type < String! > was not provided.",
                        "path": None,
                        "locations": [{"line": 1, "column": 8}],
                    }
                ],
            },
        ),
        (
            """query ($param: String!) { nonNullStringWithDefaultField(param: $param) }""",
            {"param": None},
            {
                "data": None,
                "errors": [
                    {
                        "message": "Variable < $param > of non-null type < String! > must not be null.",
                        "path": None,
                        "locations": [{"line": 1, "column": 8}],
                    }
                ],
            },
        ),
        (
            """query ($param: String!) { nonNullStringWithDefaultField(param: $param) }""",
            {"param": "varValue"},
            {
                "data": {
                    "nonNullStringWithDefaultField": "SUCCESS-varvalue-scalar-nonNullStringWithDefaultField"
                }
            },
        ),
    ],
)
async def test_coercion_non_null_string_with_default_field(
    engine, query, variables, expected
):
    assert await engine.execute(query, variables=variables) == expected