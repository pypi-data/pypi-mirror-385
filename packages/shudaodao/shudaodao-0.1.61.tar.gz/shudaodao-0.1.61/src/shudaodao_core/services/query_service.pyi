from ..exception.service_exception import (
    ValueException as ValueException,
    raise_request_validation_error as raise_request_validation_error,
)
from ..logger.logging_ import logging as logging
from ..schemas.element import Paging as Paging
from ..schemas.query_request import QueryRequest as QueryRequest
from ..tools.query_builder import QueryBuilder as QueryBuilder
from ..tools.tenant_manager import TenantManager as TenantManager
from ..type.var import SQLModelDB as SQLModelDB, SQLModelResponse as SQLModelResponse
from .data_service import DataService as DataService
from sqlalchemy import ColumnElement
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncSession
from typing import Any

class QueryService:
    @classmethod
    def check_query_request(cls, query: QueryRequest): ...
    @classmethod
    async def query_columns_first(
        cls,
        db: AsyncSession,
        *,
        model_class: type[SQLModelDB],
        condition: list[ColumnElement] | ColumnElement | any,
    ) -> SQLModelDB:
        """根据列条件查询单条记录。
        自动附加租户过滤条件。

        Args:
            db (AsyncSession): 异步数据库会话。
            model_class (Type[SQLModelDB]): 数据库模型类。
            condition (Union[List[ColumnElement], ColumnElement, Any]): 查询条件。

        Returns:
            SQLModelDB: 查询到的第一条记录，若无则返回 None（但类型提示为模型，实际可能为 None）。
        """
    @classmethod
    async def query_columns(
        cls,
        db: AsyncSession,
        *,
        model_class: type[SQLModelDB],
        condition: list[ColumnElement] | ColumnElement | any,
    ):
        """根据列条件查询单条记录。
        自动附加租户过滤条件。

        Args:
            db (AsyncSession): 异步数据库会话。
            model_class (Type[SQLModelDB]): 数据库模型类。
            condition (Union[List[ColumnElement], ColumnElement, Any]): 查询条件。

        Returns:
            SQLModelDB: 查询到的所有记录，若无则返回 None（但类型提示为模型，实际可能为 None）。
        """
    @classmethod
    def get_condition_from_columns(cls, condition, model_class): ...
    @classmethod
    async def query(
        cls,
        db: AsyncSession,
        *,
        query_request: QueryRequest,
        model_class: type[SQLModelDB],
        response_class: type[SQLModelResponse],
    ): ...
    @classmethod
    def get_order_by(cls, statement, model_class, query_sort): ...
    @classmethod
    async def get_count_where(
        cls, *, statement, model_class: type[SQLModelDB], query_request: QueryRequest
    ) -> Any: ...
    @classmethod
    async def get_where(
        cls,
        *,
        statement,
        model_class: type[SQLModelDB],
        relation_class,
        query_request: QueryRequest,
    ) -> Any: ...
    @classmethod
    async def get_select(cls, model_class, query_request: QueryRequest): ...
    @classmethod
    async def serialize_nested(
        cls,
        obj: Any,
        *,
        query_format,
        relation_fields: dict | None = None,
        with_tag: bool = False,
    ) -> Any: ...
