from pathlib import Path
from app.core.exceptions import InvalidDocumentError
from app.models.preprocessing import (
    PreprocessingResult,
    ProcessedPage,
)
from app.services.preprocessing.image import (
    decode_image,
    preprocess_image,
)
from app.services.preprocessing.pdf import render_pdf_pages

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def preprocess_document(
    file_bytes: bytes,
    filename: str,
) -> PreprocessingResult:

    extension = Path(filename).suffix.lower()

    processed_pages: list[ProcessedPage] = []

    if extension == ".pdf":
        pages = render_pdf_pages(file_bytes)

        for index, image in enumerate(pages, start=1):
            height, width = image.shape[:2]

            processed_pages.append(
                ProcessedPage(
                    page_number=index,
                    image=image,
                    width=width,
                    height=height,
                )
            )

        return PreprocessingResult(
            pages=processed_pages,
            source_type="pdf",
            page_count=len(processed_pages),
        )

    if extension in IMAGE_EXTENSIONS:
        image = decode_image(file_bytes)
        image = preprocess_image(image)

        height, width = image.shape[:2]

        processed_pages.append(
            ProcessedPage(
                page_number=1,
                image=image,
                width=width,
                height=height,
            )
        )

        return PreprocessingResult(
            pages=processed_pages,
            source_type="image",
            page_count=1,
        )

    raise InvalidDocumentError(
        f"Unsupported document extension: {extension}"
    )