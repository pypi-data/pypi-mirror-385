"""This module contains the API routes for managing tags."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field
from typing_extensions import Annotated

from lightly_studio.api.routes.api.dataset import get_and_validate_dataset_id
from lightly_studio.api.routes.api.status import (
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_CREATED,
    HTTP_STATUS_NOT_FOUND,
)
from lightly_studio.api.routes.api.validators import Paginated
from lightly_studio.db_manager import SessionDep
from lightly_studio.models.dataset import DatasetTable
from lightly_studio.models.tag import (
    TagCreate,
    TagCreateBody,
    TagTable,
    TagUpdate,
    TagUpdateBody,
    TagView,
)
from lightly_studio.resolvers import tag_resolver

tag_router = APIRouter()


@tag_router.post(
    "/datasets/{dataset_id}/tags",
    response_model=TagView,
    status_code=HTTP_STATUS_CREATED,
)
def create_tag(
    session: SessionDep,
    dataset: Annotated[
        DatasetTable,
        Path(title="Dataset Id"),
        Depends(get_and_validate_dataset_id),
    ],
    body: TagCreateBody,
) -> TagTable:
    """Create a new tag in the database."""
    dataset_id = dataset.dataset_id
    try:
        return tag_resolver.create(
            session=session,
            tag=TagCreate(**body.model_dump(exclude_unset=True), dataset_id=dataset_id),
        )
    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTP_STATUS_CONFLICT,
            detail=f"""
                Tag with name {body.name} already exists
                in the dataset {dataset_id}.
            """,
        ) from e


@tag_router.get("/datasets/{dataset_id}/tags", response_model=List[TagView])
def read_tags(
    session: SessionDep,
    dataset: Annotated[
        DatasetTable,
        Path(title="Dataset Id"),
        Depends(get_and_validate_dataset_id),
    ],
    paginated: Annotated[Paginated, Query()],
) -> list[TagTable]:
    """Retrieve a list of tags from the database."""
    return tag_resolver.get_all_by_dataset_id(
        session=session,
        dataset_id=dataset.dataset_id,
        offset=paginated.offset,
        limit=paginated.limit,
    )


@tag_router.get("/datasets/{dataset_id}/tags/{tag_id}")
def read_tag(
    session: SessionDep,
    dataset: Annotated[
        DatasetTable,
        Path(title="Dataset Id"),
        Depends(get_and_validate_dataset_id),
    ],
    tag_id: Annotated[UUID, Path(title="Tag Id")],
) -> TagTable:
    """Retrieve a single tag from the database."""
    tag = tag_resolver.get_by_id(session=session, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"""
            Tag with id {tag_id} for dataset {dataset.dataset_id} not found.
            """,
        )
    return tag


@tag_router.put("/datasets/{dataset_id}/tags/{tag_id}")
def update_tag(
    session: SessionDep,
    dataset: Annotated[
        DatasetTable,
        Path(title="Dataset Id"),
        Depends(get_and_validate_dataset_id),
    ],
    tag_id: Annotated[UUID, Path(title="Tag Id")],
    body: TagUpdateBody,
) -> TagTable:
    """Update an existing tag in the database."""
    try:
        tag = tag_resolver.update(
            session=session,
            tag_id=tag_id,
            tag_data=TagUpdate(
                **body.model_dump(exclude_unset=True),
            ),
        )
        if not tag:
            raise HTTPException(
                status_code=HTTP_STATUS_NOT_FOUND,
                detail=f"Tag with id {tag_id} not found.",
            )
    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTP_STATUS_CONFLICT,
            detail=f"""
                Cannot update tag. Tag with name {body.name}
                already exists in the dataset {dataset.dataset_id}.
            """,
        ) from e
    return tag


@tag_router.delete("/datasets/{dataset_id}/tags/{tag_id}")
def delete_tag(
    session: SessionDep,
    tag_id: Annotated[UUID, Path(title="Tag Id")],
) -> dict[str, str]:
    """Delete a tag from the database."""
    if not tag_resolver.delete(session=session, tag_id=tag_id):
        raise HTTPException(status_code=HTTP_STATUS_NOT_FOUND, detail="tag not found")
    return {"status": "deleted"}


class SampleIdsBody(BaseModel):
    """body parameters for adding or removing thing_ids."""

    sample_ids: list[UUID] | None = Field(None, description="sample ids to add/remove")


@tag_router.post(
    "/datasets/{dataset_id}/tags/{tag_id}/add/samples",
    status_code=HTTP_STATUS_CREATED,
)
def add_sample_ids_to_tag_id(
    session: SessionDep,
    # dataset_id is needed for the generator
    dataset_id: Annotated[  # noqa: ARG001
        UUID,
        Path(title="Dataset Id", description="The ID of the dataset"),
    ],
    tag_id: UUID,
    body: SampleIdsBody,
) -> bool:
    """Add sample_ids to a tag_id."""
    tag = tag_resolver.get_by_id(session=session, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Tag {tag_id} not found, can't add sample_ids.",
        )

    sample_ids = body.sample_ids if body.sample_ids else []
    tag_resolver.add_sample_ids_to_tag_id(session=session, tag_id=tag_id, sample_ids=sample_ids)
    return True


@tag_router.delete(
    "/datasets/{dataset_id}/tags/{tag_id}/remove/samples",
)
def remove_thing_ids_to_tag_id(
    session: SessionDep,
    tag_id: UUID,
    body: SampleIdsBody,
) -> bool:
    """Add thing_ids to a tag_id."""
    tag = tag_resolver.get_by_id(session=session, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Tag {tag_id} not found, can't remove samples.",
        )

    sample_ids = body.sample_ids if body.sample_ids else []
    tag_resolver.remove_sample_ids_from_tag_id(
        session=session, tag_id=tag_id, sample_ids=sample_ids
    )
    return True


class AnnotationIdsBody(BaseModel):
    """body parameters for adding or removing annotation_ids."""

    annotation_ids: list[UUID] | None = Field(None, description="annotation ids to add/remove")


@tag_router.post(
    "/datasets/{dataset_id}/tags/{tag_id}/add/annotations",
    status_code=HTTP_STATUS_CREATED,
)
def add_annotation_ids_to_tag_id(
    session: SessionDep,
    # dataset_id is needed for the generator
    dataset_id: Annotated[  # noqa: ARG001
        UUID,
        Path(title="Dataset Id", description="The ID of the dataset"),
    ],
    tag_id: UUID,
    body: AnnotationIdsBody,
) -> bool:
    """Add thing_ids to a tag_id."""
    tag = tag_resolver.get_by_id(session=session, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Tag {tag_id} not found, can't add annotations.",
        )

    annotation_ids = body.annotation_ids if body.annotation_ids else []
    tag_resolver.add_annotation_ids_to_tag_id(
        session=session, tag_id=tag_id, annotation_ids=annotation_ids
    )
    return True


@tag_router.delete(
    "/datasets/{dataset_id}/tags/{tag_id}/remove/annotations",
)
def remove_annotation_ids_to_tag_id(
    session: SessionDep,
    tag_id: UUID,
    body: AnnotationIdsBody,
) -> bool:
    """Add thing_ids to a tag_id."""
    tag = tag_resolver.get_by_id(session=session, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Tag {tag_id} not found, can't remove annotations.",
        )

    annotation_ids = body.annotation_ids if body.annotation_ids else []
    tag_resolver.remove_annotation_ids_from_tag_id(
        session=session, tag_id=tag_id, annotation_ids=annotation_ids
    )
    return True
