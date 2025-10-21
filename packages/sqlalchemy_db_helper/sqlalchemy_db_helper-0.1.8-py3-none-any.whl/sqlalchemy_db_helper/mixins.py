__all__ = (
    "CRUDMixin",
    "UUIDPKMixin",
    "ReprMixin",
    "PaginationMixin",
)

from typing import Any, AsyncGenerator, Sequence, TypeVar
from uuid import UUID, uuid4

from sqlalchemy import UUID as SA_UUID, text
from sqlalchemy import ScalarResult, Select
from sqlalchemy import delete as sa_delete
from sqlalchemy import func
from sqlalchemy import select as sa_select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .schemas import PaginationModel, PaginationResultModel

T = TypeVar("T", bound=DeclarativeBase)

DEFAULT_LIMIT: int = 1000
DEFAULT_ORDERING: str = "id"
DEFAULT_MAX_PAGES: int = 1000


class CRUDMixin:
    __table__: type[T]

    def __init__(self, async_session: AsyncSession) -> None:
        self.async_session = async_session

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(ORM obj={self.__table__})"

    def __repr__(self) -> str:
        return f"'{self.__str__()}'"

    async def count(self, stmt: Select, params: dict | None = None) -> int:
        if hasattr(stmt, "subquery"):
            count_stmt = sa_select(func.count()).select_from(stmt.subquery())
            result = await self.async_session.scalar(count_stmt)
        else:
            params = params or {}
            count_sql = f"SELECT COUNT(*) FROM ({stmt.text if hasattr(stmt, 'text') else stmt}) AS sub"
            result = await self.async_session.scalar(
                text(count_sql).bindparams(**params)
            )

        await self.async_session.commit()
        return result

    async def update(self, instances: list[dict]) -> None:
        stmt = sa_update(self.__table__)
        await self.async_session.execute(stmt, instances)
        await self.async_session.commit()

    async def create(self, instances: list[dict | T]) -> list[T]:
        items: list[T] = [
            self.__table__(**instance) if isinstance(instance, dict) else instance
            for instance in instances
        ]
        self.async_session.add_all(items)
        await self.async_session.commit()
        return items

    async def delete(self, where: list | tuple) -> None:
        stmt = sa_delete(self.__table__).where(*where)
        await self.async_session.execute(stmt)
        await self.async_session.commit()


class UUIDPKMixin:
    id: Mapped[UUID] = mapped_column(
        SA_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


class ReprMixin:
    repr_col_num: int = 3
    repr_cols: frozenset = frozenset()

    def __str__(self) -> str:
        cols = []

        for idx, col in enumerate(self.__table__.columns.keys()):  # type: ignore
            if self.repr_cols:
                if col in self.repr_cols:
                    cols.append(f"{col}={getattr(self, col)}")

            else:
                if idx < self.repr_col_num:
                    cols.append(f"{col}={getattr(self, col)}")

        return f"{self.__class__.__name__}({', '.join(cols)})"

    def __repr__(self) -> str:
        return f"'{self.__str__()}'"


class PaginationMixin(CRUDMixin):
    @classmethod
    def build_pagination(
        cls,
        limit: int,
        page: int,
        rows_count: int,
    ) -> PaginationModel:
        pages = rows_count // limit
        total_pages = pages if rows_count % limit == 0 else pages + 1

        pagination_dict = {
            "total": rows_count,
            "page": page,
            "per_page": limit,
            "total_pages": total_pages,
        }

        return PaginationModel.model_validate(pagination_dict)

    async def paginated_result(
        self,
        stmt: Any,
        page: int,
        limit: int | None = None,
        order_by: Any | None = None,
        *,
        params: dict | None = None,
    ) -> PaginationResultModel:
        if limit is None:
            limit = DEFAULT_LIMIT

        if order_by is None:
            order_by = DEFAULT_ORDERING

        rows_count = await self.count(stmt, params)

        result = {}
        offset = (page - 1) * limit

        if rows_count > limit:
            result["pagination"] = self.build_pagination(limit, page, rows_count)

        result["data"] = await self.__limited_scalars(stmt, limit, offset, order_by)
        return PaginationResultModel.model_validate(result)

    async def __limited_scalars(
        self,
        stmt: Any,
        limit: int,
        offset: int,
        order_by: Any,
        *,
        params: dict | None = None,
    ) -> ScalarResult:
        if hasattr(stmt, "limit"):
            result = await self.async_session.scalars(
                stmt.limit(limit).offset(offset).order_by(order_by)
            )
        else:
            sql_text = stmt.text if hasattr(stmt, "text") else stmt
            order_sql = f" ORDER BY {order_by}" if order_by else ""
            paginated_sql = f"SELECT * FROM ({sql_text}) AS sub{order_sql} LIMIT :limit OFFSET :offset"
            final_stmt = text(paginated_sql).bindparams(
                **params,
                limit=limit,
                offset=offset,
            )
            result = await self.async_session.scalars(final_stmt)

        await self.async_session.commit()
        return result

    @classmethod
    async def _get_paginated_result(
        cls,
        db_method,
        total_pages: int,
        **load_options,
    ) -> AsyncGenerator[PaginationResultModel[T], None]:
        for page in range(2, total_pages + 1):
            load_options.update({"page": page})
            yield await db_method(**load_options)

    async def aiter_load(
        self,
        db_method,
        *,
        max_pages: int | None = DEFAULT_MAX_PAGES,
        per_page: int = DEFAULT_LIMIT,
        **load_options,
    ) -> AsyncGenerator[Sequence[T], None]:  # Note: Количество подгружаемых строк (см)
        result = await db_method(**load_options)  # type: PaginationResultModel
        data = result.data.all()

        if not data:
            return

        yield data

        if not result.pagination:
            return

        if max_pages is None or result.pagination.total_pages <= max_pages:
            total_pages = result.pagination.total_pages

        else:
            total_pages = max_pages

        load_options["limit"] = per_page

        async for paginated_result in self._get_paginated_result(
            db_method,
            total_pages,
            **load_options,
        ):
            yield paginated_result.data.all()
