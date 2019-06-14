from inspect import isclass

from tartiflette.schema.registry import SchemaRegistry
from tartiflette.types.exceptions.tartiflette import (
    MissingImplementation,
    UnknownScalarDefinition,
)


class Scalar:
    """
    This decorator allows you to link a GraphQL Scalar to a Scalar class.

    For example, for the following SDL:

        scalar DateTime

    Use the Directive decorator the following way:

        @Scalar("DateTime")
        class ScalarDateTime:
            @staticmethod
            def coerce_output(value):
                return value.isoformat()

            @staticmethod
            def coerce_input(value):
                return iso8601.parse_date(value)
    """

    def __init__(self, name: str, schema_name: str = "default") -> None:
        """
        TODO:
        :param name: TODO:
        :param schema_name: TODO:
        :type name: TODO:
        :type schema_name: TODO:
        """
        self.name = name
        self._implementation = None
        self._schema_name = schema_name

    def bake(self, schema: "GraphQLSchema") -> None:
        """
        TODO:
        :param schema: TODO:
        :type schema: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        if not self._implementation:
            raise MissingImplementation(
                "No implementation given for scalar < %s >" % self.name
            )

        scalar = schema.find_scalar(self.name)
        if not scalar:
            raise UnknownScalarDefinition(
                "Unknow Scalar Definition %s" % self.name
            )

        scalar.coerce_output = self._implementation.coerce_output
        scalar.coerce_input = self._implementation.coerce_input
        scalar.parse_literal = self._implementation.parse_literal

    def __call__(self, implementation):
        """
        TODO:
        :param implementation: TODO:
        :type implementation: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        if isclass(implementation):
            self._implementation = implementation()
        else:
            self._implementation = implementation
        SchemaRegistry.register_scalar(self._schema_name, self)
        return implementation
