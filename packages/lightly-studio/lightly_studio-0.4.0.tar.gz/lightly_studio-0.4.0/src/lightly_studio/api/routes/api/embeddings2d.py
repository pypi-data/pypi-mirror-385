"""Routes delivering 2D embeddings for visualization."""

from __future__ import annotations

import io
from uuid import UUID

import pyarrow as pa
from fastapi import APIRouter, HTTPException, Response
from pyarrow import ipc
from pydantic import BaseModel, Field
from sqlmodel import select

from lightly_studio.db_manager import SessionDep
from lightly_studio.models.dataset import DatasetTable
from lightly_studio.models.embedding_model import EmbeddingModelTable
from lightly_studio.resolvers import sample_embedding_resolver, sample_resolver
from lightly_studio.resolvers.samples_filter import SampleFilter
from lightly_studio.resolvers.twodim_embedding_resolver import _calculate_2d_embeddings

embeddings2d_router = APIRouter()


class GetEmbeddings2DRequest(BaseModel):
    """Request body for retrieving 2D embeddings."""

    filters: SampleFilter | None = Field(
        None,
        description="Filter parameters identifying matching samples",
    )


@embeddings2d_router.post("/embeddings2d/default")
def get_2d_embeddings(
    session: SessionDep,
    body: GetEmbeddings2DRequest | None = None,
) -> Response:
    """Return 2D embeddings serialized as an Arrow stream."""
    # TODO(Malte, 09/2025): Support choosing the dataset via API parameter.
    dataset = session.exec(select(DatasetTable).limit(1)).first()
    if dataset is None:
        raise HTTPException(status_code=404, detail="No dataset configured.")

    # TODO(Malte, 09/2025): Support choosing the embedding model via API parameter.
    embedding_model = session.exec(
        select(EmbeddingModelTable)
        .where(EmbeddingModelTable.dataset_id == dataset.dataset_id)
        .limit(1)
    ).first()
    if embedding_model is None:
        raise HTTPException(status_code=404, detail="No embedding model configured.")

    embeddings = sample_embedding_resolver.get_all_by_dataset_id(
        session=session,
        dataset_id=dataset.dataset_id,
        embedding_model_id=embedding_model.embedding_model_id,
    )

    planar_embeddings = _calculate_2d_embeddings([e.embedding for e in embeddings])
    # TODO(lukas 10/2025): This can become very slow for large datasets, we should consider using
    # `pa.chunked_array` to directly construct the xy array.
    x = (x for (x, _) in planar_embeddings)
    y = (y for (_, y) in planar_embeddings)

    matching_sample_ids: set[UUID] | None = None
    filters = body.filters if body else None
    if filters:
        matching_samples_result = sample_resolver.get_all_by_dataset_id(
            session=session,
            dataset_id=dataset.dataset_id,
            filters=filters,
        )
        matching_sample_ids = {sample.sample_id for sample in matching_samples_result.samples}

    sample_ids = [embedding.sample_id for embedding in embeddings]
    if matching_sample_ids is None:
        fulfils_filter = [1] * len(sample_ids)
    else:
        fulfils_filter = [1 if sample_id in matching_sample_ids else 0 for sample_id in sample_ids]

    # TODO(Malte, 09/2025): Save the 2D-embeddings in the database to avoid recomputing
    # them on every request.

    # TODO(Malte, 09/2025): Include a sample identifier in the returned payload.
    table = pa.table(
        {
            "x": pa.array(x, type=pa.float32()),
            "y": pa.array(y, type=pa.float32()),
            "fulfils_filter": pa.array(fulfils_filter, type=pa.uint8()),
            "sample_id": pa.array([str(sample_id) for sample_id in sample_ids], type=pa.string()),
        }
    )

    buffer = io.BytesIO()
    with ipc.new_stream(buffer, table.schema) as writer:
        writer.write_table(table)
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.apache.arrow.stream",
        headers={
            "Content-Disposition": "inline; filename=embeddings2d.arrow",
            "Content-Type": "application/vnd.apache.arrow.stream",
            "X-Content-Type-Options": "nosniff",
        },
    )
