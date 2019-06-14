from typing import Callable, Optional

from tartiflette.schema import GraphQLSchema
from tartiflette.schema.registry import SchemaRegistry
from tartiflette.sdl.builder import build_graphql_schema_from_sdl

_SCHEMA_OBJECT_IDS = ["directives", "resolvers", "scalars", "subscriptions"]


class SchemaBakery:
    """
    TODO:
    """

    @staticmethod
    def _preheat(schema_name: str) -> GraphQLSchema:
        """
        TODO:
        :param schema_name: TODO:
        :type schema_name: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        schema_info = SchemaRegistry.find_schema_info(schema_name)
        schema = schema_info.get("inst", GraphQLSchema(name=schema_name))

        sdl = schema_info["sdl"]
        build_graphql_schema_from_sdl(sdl, schema=schema)

        for object_ids in _SCHEMA_OBJECT_IDS:
            for obj in schema_info.get(object_ids, {}).values():
                obj.bake(schema)

        schema_info["inst"] = schema

        return schema

    @staticmethod
    def bake(
        schema_name: str, custom_default_resolver: Optional[Callable] = None
    ) -> GraphQLSchema:
        """
        TODO:
        :param schema_name: TODO:
        :param custom_default_resolver: TODO:
        :type schema_name: TODO:
        :type custom_default_resolver: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        schema = SchemaBakery._preheat(schema_name)
        schema.bake(custom_default_resolver)
        return schema
