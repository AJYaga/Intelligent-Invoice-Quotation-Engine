from pathlib import Path
from app.core.exceptions import (
    InvalidDocumentError,
    UnsupportedFileTypeError,
)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}

def validate_upload(
    filename: str,
    content: bytes,
    max_size_mb: int,
) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            "Unsupported file type. "
            "Allowed: PDF, JPG, JPEG, PNG."
        )

    if not content:
        raise InvalidDocumentError(
            "Uploaded file is empty."
        )

    max_size_bytes = (
        max_size_mb
        * 1024
        * 1024
    )

    if len(content) > max_size_bytes:
        raise InvalidDocumentError(
            f"File exceeds the "
            f"{max_size_mb} MB limit."
        )

    return extension