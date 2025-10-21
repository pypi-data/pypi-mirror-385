"""This module contains the API routes for managing text embedding."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from typing_extensions import Annotated

from lightly_studio.api.routes.api.status import (
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
)
from lightly_studio.dataset.embedding_manager import (
    EmbeddingManager,
    EmbeddingManagerProvider,
    TextEmbedQuery,
)

text_embedding_router = APIRouter()
# Define a type alias for the EmbeddingManager dependency
EmbeddingManagerDep = Annotated[
    EmbeddingManager,
    Depends(lambda: EmbeddingManagerProvider.get_embedding_manager()),
]


@text_embedding_router.get("/text_embedding/embed_text", response_model=List[float])
def embed_text(
    embedding_manager: EmbeddingManagerDep,
    query_text: str = Query(..., description="The text to embed."),
    embedding_model_id: Annotated[
        UUID | None,
        Query(..., description="The ID of the embedding model to use."),
    ] = None,
) -> list[float]:
    """Retrieve embeddings for the input text."""
    try:
        text_embeddings = embedding_manager.embed_text(
            TextEmbedQuery(query_text, embedding_model_id)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=HTTP_STATUS_INTERNAL_SERVER_ERROR,
            detail=f"{exc}",
        ) from None

    return text_embeddings
