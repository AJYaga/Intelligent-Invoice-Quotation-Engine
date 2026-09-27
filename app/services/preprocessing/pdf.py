import cv2
import pymupdf
import numpy as np
from app.core.exceptions import InvalidDocumentError
from app.services.preprocessing.image import preprocess_image

def render_pdf_pages(file_bytes: bytes) -> list[np.ndarray]:
    try:
        document = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise InvalidDocumentError(
            "Unable to open PDF. The document may be corrupt."
        ) from exc

    if document.page_count == 0:
        document.close()
        raise InvalidDocumentError("PDF contains no pages.")

    pages: list[np.ndarray] = []

    try:
        for page in document:
            matrix = pymupdf.Matrix(2.0, 2.0)

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )

            image_data = np.frombuffer(
                pixmap.samples,
                dtype=np.uint8,
            )

            image = image_data.reshape(
                pixmap.height,
                pixmap.width,
                pixmap.n,
            )

            if pixmap.n == 3:
                image = cv2.cvtColor(
                    image,
                    cv2.COLOR_RGB2BGR,
                )
            elif pixmap.n == 4:
                image = cv2.cvtColor(
                    image,
                    cv2.COLOR_RGBA2BGR,
                )

            processed = preprocess_image(image)

            pages.append(processed)

    except Exception as exc:
        raise InvalidDocumentError(
            "Unable to render one or more PDF pages."
        ) from exc

    finally:
        document.close()

    return pages