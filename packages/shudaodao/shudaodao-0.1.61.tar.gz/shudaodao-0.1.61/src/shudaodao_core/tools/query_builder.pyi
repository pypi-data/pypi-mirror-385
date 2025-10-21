from ..exception.service_exception import ValueException as ValueException
from ..logger.logging_ import logging as logging
from ..schemas.query_request import (
    Condition as Condition,
    Filter as Filter,
    FilterGroup as FilterGroup,
)
from ..services.enum_service import EnumService as EnumService
from .query_field import (
    convert_datetime_iso_to_standard as convert_datetime_iso_to_standard,
    format_enum as format_enum,
    get_enum_field_names as get_enum_field_names,
)
from sqlalchemy import ColumnElement as ColumnElement
from typing import Any

class QueryBuilder:
    @classmethod
    def get_condition(
        cls,
        *,
        model_class,
        is_relation: bool,
        field_name: str,
        field_op: str,
        field_val: str | int | float | bool | list | None,
    ): ...
    @staticmethod
    def get_condition_python_value(field, field_type, field_value): ...
    @classmethod
    async def get_relation_where(
        cls, *, relation_class: dict, filter_obj: Filter | list
    ): ...
    @classmethod
    async def get_table_where(
        cls, *, model_class, filter_obj: Filter | list, is_relation: bool = False
    ) -> ColumnElement | None:
        """主表的查询条件"""
    @classmethod
    async def get_query_relation(
        cls, model_class, model_name, include_path, query_format, query_tags
    ): ...
    @classmethod
    async def deep_serialize_sqlmodel(
        cls,
        obj: Any,
        *,
        query_format,
        relation_fields: dict | None = None,
        tag_name=None,
    ) -> Any: ...
    @classmethod
    def sqlmodel_format_datetime(cls, value): ...
    @classmethod
    def format_enum(
        cls, enum_fields, field_value, item_dict, key, model_class
    ) -> None: ...
