"""Common type definitions for the lightly_studio package."""

from pathlib import Path
from typing import TypeVar, Union
from uuid import UUID

from sqlmodel.sql.expression import SelectOfScalar

from lightly_studio.models.annotation.annotation_base import AnnotationBaseTable
from lightly_studio.models.sample import SampleTable

# Generic query type for filters that work with both data queries and count queries
QueryType = TypeVar(
    "QueryType",
    SelectOfScalar[AnnotationBaseTable],
    SelectOfScalar[SampleTable],
    SelectOfScalar[int],
    SelectOfScalar[UUID],
)

PathLike = Union[str, Path]
