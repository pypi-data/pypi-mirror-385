"""
Base model classes for SQLAlchemy models.
"""
import logging
from typing import Any, Type, TypeVar, Dict
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import Select

from .base_protocol import BaseModel

def create_declerative_base(name: str = "db") -> Type[BaseModel]:
    """
    Declarative base class factory that returns a type
    satisfying the BaseModel.

    :param str name: The name of the associated database. The argument passed when creating the db extension instance.
    """
    base = declarative_base()

    class DeclarativeBase(base, BaseModel):  # type: ignore
        """
        Base model from sqlalchemy.orm with
        query classmethod
        """
        __abstract__ = True

        __db_name__: str = name

        @classmethod
        def query(cls, session: AsyncSession) -> "AsyncQuery":
            """
            Creates an AsyncQuery instance
            """
            return AsyncQuery(session, cls)

        @classmethod
        def db_name(cls) -> str:
            return cls.__db_name__

    return DeclarativeBase

#pylint: disable-next=C0103
_T0 = TypeVar("_T0", bound=Any)

class AsyncQuery:
    """
    Async-friendly intuitive query object.
    Easy and intuitive querying with pagination support.
    """

    def __init__(self, session: AsyncSession, model: Type[_T0]):
        self.session = session
        self.model = model
        self._query: Select = select(model)  # Start with SELECT * FROM table

    def where(self, *conditions) -> "AsyncQuery":
        """Adds WHERE conditions (same as `filter()`)."""
        return self.filter(*conditions)

    def filter(self, *conditions) -> "AsyncQuery":
        """Adds WHERE conditions to the query (supports multiple conditions)."""
        self._query = self._query.filter(*conditions)
        return self

    def filter_by(self, **kwargs) -> "AsyncQuery":
        """Adds WHERE conditions using keyword arguments (simpler syntax)."""
        self._query = self._query.filter_by(**kwargs)
        return self

    def join(self, other_model: Type[_T0]) -> "AsyncQuery":
        """Performs a SQL JOIN with another model."""
        self._query = self._query.join(other_model)
        return self

    def limit(self, num: int) -> "AsyncQuery":
        """Limits the number of results returned."""
        self._query = self._query.limit(num)
        return self

    def offset(self, num: int) -> "AsyncQuery":
        """Skips a certain number of results (used for pagination)."""
        self._query = self._query.offset(num)
        return self

    def order_by(self, *columns) -> "AsyncQuery":
        """Sorts results based on one or more columns."""
        self._query = self._query.order_by(*columns)
        return self
    
    def like(self, column, pattern, escape=None) -> "AsyncQuery":
        """
        Filters results using a SQL LIKE condition.

        :param column: A column attribute, e.g. User.name
        :param pattern: The pattern string (with % wildcards)
        :param escape: The escape character, if needed.
        :return: self, for chaining
        """
        self._query = self._query.filter(column.like(pattern, escape=escape))
        return self

    def ilike(self, column, pattern, escape=None) -> "AsyncQuery":
        """
        Filters results using a case-insensitive LIKE (ILIKE) condition.
        (Supported by Postgres, some other dialects).

        :param column: A column attribute, e.g. User.name
        :param pattern: The pattern string (with % wildcards)
        :param escape: The escape character, if needed.
        :return: self, for chaining
        """
        self._query = self._query.filter(column.ilike(pattern, escape=escape))
        return self

    async def count(self) -> int:
        """
        Returns the total number of records matching the current query,
        preserving any applied filters.
        """
        count_query = select(func.count()).select_from(self.model)
        # Apply existing filters
        if hasattr(self._query, "whereclause") and self._query.whereclause is not None:
            count_query = count_query.where(self._query.whereclause)
        self._query = count_query
        result = await self._execute_query()
        result: int = result.scalar() or 0
        return result

    async def paginate(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Paginates results.
        page (int): The page number (1-based index).
        per_page (int): Number of results per page.
        ```
        Returns:
            dict: {
                "items": List of results,
                "total": Total records,
                "page": Current page,
                "pages": Total pages,
                "per_page": Results per page,
                "has_next": Whether there's a next page,
                "has_prev": Whether there's a previous page
            }
        ```
        """
        page = max(page, 1)

        total_records = await self.count()
        total_pages = (total_records + per_page - 1) // per_page  # Round up division

        self._query = self._query.limit(per_page).offset((page - 1) * per_page)
        result = await self._execute_query()
        items = result.scalars().all()
        #await self.session.close()

        return {
            "items": items,
            "total": total_records,
            "page": page,
            "pages": total_pages,
            "per_page": per_page,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    async def _execute_query(self) -> Any:
        """Executes the query safely with automatic rollback on failure."""
        try:
            result = await self.session.execute(self._query)
            return result
        except SQLAlchemyError as e:
            await self.session.rollback()
            logging.error("Database query failed: %s", e)
            raise

    async def all(self) -> list:
        """Executes the query and returns all results."""
        result = await self._execute_query()
        return result.scalars().all()

    async def first(self) -> Any:
        """Executes the query and returns the first result."""
        result = await self._execute_query()
        return result.scalars().first()

    async def one(self) -> Any:
        """Executes the query and expects exactly one result."""
        result = await self._execute_query()
        return result.scalars().one()

