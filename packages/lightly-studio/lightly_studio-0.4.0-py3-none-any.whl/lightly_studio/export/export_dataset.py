"""Exports datasets from Lightly Studio into various formats."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from labelformat.formats import COCOObjectDetectionOutput
from sqlmodel import Session

from lightly_studio.core.sample import Sample
from lightly_studio.export.lightly_studio_label_input import LightlyStudioObjectDetectionInput
from lightly_studio.type_definitions import PathLike

DEFAULT_EXPORT_FILENAME = "coco_export.json"


class DatasetExport:
    """Provides methods to export a dataset or a subset of it.

    This class is typically not instantiated directly but returned by `Dataset.export()`.
    It allows exporting data in various formats.
    """

    def __init__(self, session: Session, samples: Iterable[Sample]):
        """Initializes the DatasetExport object.

        Args:
            session: The database session.
            samples: Samples to export.
        """
        self.session = session
        self.samples = samples

    def to_coco_object_detections(self, output_json: PathLike | None = None) -> None:
        """Exports object detection annotations to a COCO format JSON file.

        Args:
            output_json: The path to the output COCO JSON file. If not provided,
                defaults to "coco_export.json" in the current working directory.

        Raises:
            ValueError: If the annotation task with the given name does not exist.
        """
        if output_json is None:
            output_json = DEFAULT_EXPORT_FILENAME
        to_coco_object_detections(
            session=self.session,
            samples=self.samples,
            output_json=Path(output_json),
        )


def to_coco_object_detections(
    session: Session,
    samples: Iterable[Sample],
    output_json: Path,
) -> None:
    """Exports object detection annotations to a COCO format JSON file.

    This function is for internal use. Use `Dataset.query().export().to_coco_object_detections()`
    instead.

    Args:
        session: The database session.
        samples: The samples to export.
        output_json: The path to save the output JSON file.
    """
    export_input = LightlyStudioObjectDetectionInput(
        session=session,
        samples=samples,
    )
    COCOObjectDetectionOutput(output_file=output_json).save(label_input=export_input)
