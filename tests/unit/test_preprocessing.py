import cv2
import numpy as np
import pytest
from app.core.exceptions import InvalidDocumentError
from app.services.preprocessing.image import (
    decode_image,
    preprocess_image,
)
from app.services.preprocessing.orientation import rotate_image
import pymupdf
from app.services.preprocessing.pdf import render_pdf_pages

def create_test_image() -> np.ndarray:
    image = np.ones(
        (100, 200, 3),
        dtype=np.uint8,
    ) * 255

    cv2.putText(
        image,
        "TEST",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 0),
        2,
    )

    return image

def test_decode_valid_png():
    image = create_test_image()

    success, encoded = cv2.imencode(
        ".png",
        image,
    )

    assert success

    decoded = decode_image(
        encoded.tobytes()
    )

    assert decoded is not None
    assert decoded.shape[0] == 100
    assert decoded.shape[1] == 200

def test_decode_corrupt_image():
    corrupt_data = b"this-is-not-an-image"

    with pytest.raises(InvalidDocumentError):
        decode_image(corrupt_data)

def test_preprocess_returns_grayscale():
    image = create_test_image()

    processed = preprocess_image(image)

    assert len(processed.shape) == 2

def test_rotate_90_degrees():
    image = create_test_image()

    rotated = rotate_image(
        image,
        90,
    )

    assert rotated.shape[0] == 200
    assert rotated.shape[1] == 100

def create_test_pdf() -> bytes:
    document = pymupdf.open()

    page = document.new_page(
        width=595,
        height=842,
    )

    page.insert_text(
        (72, 100),
        "Test Invoice",
        fontsize=20,
    )

    pdf_bytes = document.tobytes()

    document.close()

    return pdf_bytes

def test_render_valid_pdf():
    pdf_bytes = create_test_pdf()

    pages = render_pdf_pages(pdf_bytes)

    assert len(pages) == 1
    assert pages[0] is not None
    assert pages[0].size > 0

def test_corrupt_pdf_rejected():
    corrupt_pdf = b"not-a-real-pdf"

    with pytest.raises(InvalidDocumentError):
        render_pdf_pages(corrupt_pdf)