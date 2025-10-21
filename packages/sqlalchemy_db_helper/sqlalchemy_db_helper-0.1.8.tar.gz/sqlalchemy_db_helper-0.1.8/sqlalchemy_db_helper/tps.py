__all__ = (
    "str_100",
    "str_500",
    "str_1000",
    "timestamp",
    "obj_path",
    "list_str",
    "list_int",
)
from datetime import datetime
from pathlib import Path
from typing import Annotated

from sqlalchemy import JSON, TIMESTAMP, String, TypeDecorator
from sqlalchemy.orm import mapped_column


class PathType(TypeDecorator):
    impl = String

    def process_bind_param(self, value: Path | None, dialect) -> str | None:
        return str(value).replace("\\", "/") if value is not None else None

    def process_result_value(self, value: str | None, dialect) -> Path | None:
        return Path(value) if value is not None else None


str_100 = Annotated[str, 100]
str_500 = Annotated[str, 500]
str_1000 = Annotated[str, 1000]

timestamp = Annotated[datetime, mapped_column(TIMESTAMP)]

obj_path = Annotated[Path, mapped_column(PathType())]

list_str = Annotated[list[str], mapped_column(JSON)]
list_int = Annotated[list[int], mapped_column(JSON)]
