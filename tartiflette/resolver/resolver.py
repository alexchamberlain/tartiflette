from inspect import iscoroutinefunction
from typing import Callable

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
                "No implementation given for resolver < %s >" % self.name
            )

        try:
            field = schema.get_field_by_name(self.name)
            field.resolver.update_func(self._implementation)
            field.raw_resolver = self._implementation
        except KeyError:
            raise UnknownFieldDefinition(
                "Unknown Field Definition %s" % self.name
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
                "The resolver `{}` given is not awaitable.".format(
                    repr(resolver)
                )
            )

        SchemaRegistry.register_resolver(self._schema_name, self)
        self._implementation = resolver
        return resolver
