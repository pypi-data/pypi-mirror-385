import polars as pl
from _typeshed import Incomplete
from contextlib import contextmanager
from datahub.utils.logger import logger as logger
from sqlalchemy.engine import Connection as Connection, Engine as Engine
from sqlalchemy.orm import Session as Session
from typing import Any, Generator, Literal

class Database:
    engine: Incomplete
    metadata: Incomplete
    schema: Incomplete
    session_factory: Incomplete
    def __init__(self, connection_string: str, pool_size: int = 3, max_overflow: int = 10, pool_timeout: int = 30, pool_recycle: int = 3600) -> None: ...
    def insert_many(self, table_name: str, data: list[dict[str, Any]]) -> int:
        """
        批量插入数据

        :param table_name: 表名
        :param data: 要插入的数据列表
        :return: 影响的行数
        """
    def query(self, sql: str, return_format: Literal['dataframe', 'records'] = 'dataframe') -> pl.DataFrame | list[dict] | None:
        """
        执行原生SQL查询

        :param sql: SQL查询语句
        :param return_format: 返回格式
        :return: 查询结果
        """
    @contextmanager
    def get_session(self) -> Generator[Session, Any, None]:
        """获取一个数据库会话，支持用户手动管理 session 生命周期"""
    def query_with_session(self, sql: str, session: Session, return_format: Literal['dataframe', 'records'] = 'dataframe'):
        """
        执行原生SQL查询

        :param sql: SQL查询语句
        :param session: 数据库会话
        :param return_format: 返回格式
        :return: 查询结果
        """
