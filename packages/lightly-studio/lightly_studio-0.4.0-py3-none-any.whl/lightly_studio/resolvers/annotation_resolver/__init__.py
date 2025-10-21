"""Resolvers for database operations."""

from lightly_studio.resolvers.annotation_resolver.count_annotations_by_dataset import (
    count_annotations_by_dataset,
)
from lightly_studio.resolvers.annotation_resolver.create_many import create_many
from lightly_studio.resolvers.annotation_resolver.delete_annotation import (
    delete_annotation,
)
from lightly_studio.resolvers.annotation_resolver.delete_annotations import (
    delete_annotations,
)
from lightly_studio.resolvers.annotation_resolver.get_all import get_all
from lightly_studio.resolvers.annotation_resolver.get_by_id import get_by_id, get_by_ids
from lightly_studio.resolvers.annotation_resolver.update_annotation_label import (
    update_annotation_label,
)
from lightly_studio.resolvers.annotation_resolver.update_bounding_box import (
    update_bounding_box,
)

__all__ = [
    "count_annotations_by_dataset",
    "create_many",
    "delete_annotation",
    "delete_annotations",
    "get_all",
    "get_by_id",
    "get_by_ids",
    "update_annotation_label",
    "update_bounding_box",
]
