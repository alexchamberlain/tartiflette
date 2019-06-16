from inspect import iscoroutinefunction
from typing import Callable, Optional

from tartiflette.schema.registry import SchemaRegistry
from tartiflette.types.exceptions.tartiflette import (
    MissingImplementation,
    NonAwaitableResolver,
    UnknownFieldDefinition,
)


class Resolver:
    """
    This decorator allows you to link a GraphQL Schema field to a resolver.

    For example, for the following SDL:

        type SomeObject {
            field: Int
        }

    Use the Resolver decorator the following way:

        @Resolver("SomeObject.field")
        async def field_resolver(parent, arguments, request_ctx, info):
            do your stuff
            return 42
    """

    def __init__(
        self,
        name: str,
        schema_name: str = "default",
        type_resolver: Optional[Callable] = None,
    ) -> None:
        """
        TODO:
        :param name: TODO:
        :param schema_name: TODO:
        :param schema_name: TODO:
        :type name: TODO:
        :type schema_name: TODO:
        """
        self.name = name
        self._type_resolver = type_resolver
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
                f"No implementation given for resolver < {self.name} >"
            )

        try:
            field = schema.get_field_by_name(self.name)
            field.raw_resolver = self._implementation
            # TODO: shouldn't we raise an exception if `type_resolver` is
            # defined for something else than an abstract type field?
            field.type_resolver = self._type_resolver
        except KeyError:
            raise UnknownFieldDefinition(
                f"Unknown Field Definition {self.name}"
            )

    def __call__(self, resolver: Callable) -> Callable:
        """
        TODO:
        :param resolver: TODO:
        :type resolver: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        if not iscoroutinefunction(resolver):
            raise NonAwaitableResolver(
                f"The resolver `{repr(resolver)}` given is not awaitable."
            )

        if self._type_resolver and not iscoroutinefunction(
            self._type_resolver
        ):
            raise NonAwaitableResolver(
                f"The type resolver `{repr(resolver)}` given is not "
                "awaitable."
            )

        SchemaRegistry.register_resolver(self._schema_name, self)
        self._implementation = resolver
        return resolver
