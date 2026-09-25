import cv2
import numpy as np
import pytest
from app.core.exceptions import InvalidDocumentError
from app.services.preprocessing.processor import preprocess_document

def test_preprocess_png_document():
    image = np.ones(
        (100, 200, 3),
        dtype=np.uint8,
    ) * 255

    success, encoded = cv2.imencode(
        ".png",
        image,
    )

    assert success

    result = preprocess_document(
        encoded.tobytes(),
        "invoice.png",
    )

    assert result.source_type == "image"
    assert result.page_count == 1
    assert len(result.pages) == 1

def test_corrupt_png_document():
    with pytest.raises(InvalidDocumentError):
        preprocess_document(
            b"fake-data",
            "invoice.png",
        )