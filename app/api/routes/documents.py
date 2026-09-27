from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.core.config import settings
import logging
from fastapi import Depends
from app.api.dependencies import get_document_pipeline
from app.api.serializers import serialize_pipeline_result
from app.core.exceptions import DocumentProcessingError
from app.models.response import DocumentAnalysisResponse
from app.pipeline.document_pipeline import DocumentPipeline

router = APIRouter(prefix="/api/documents", tags=["Documents"])
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
logger = logging.getLogger(__name__)

@router.post("/validate-upload")
async def validate_upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Allowed: PDF, JPG, JPEG, PNG.",
        )

    content = await file.read()

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.max_upload_size_mb} MB limit.",
        )

    return {
        "filename": file.filename,
        "extension": extension,
        "size_bytes": len(content),
        "valid": True,
    }

@router.post(
    "/analyze",
    response_model=DocumentAnalysisResponse,
)
async def analyze_document(
    file: UploadFile = File(...),
    pipeline: DocumentPipeline = Depends(
        get_document_pipeline
    ),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Unsupported file type. "
                "Allowed: PDF, JPG, JPEG, PNG."
            ),
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    max_size_bytes = (
        settings.max_upload_size_mb
        * 1024
        * 1024
    )

    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File exceeds the "
                f"{settings.max_upload_size_mb} MB limit."
            ),
        )

    try:
        result = pipeline.analyze(
            file_bytes=content,
            filename=file.filename,
        )
    except DocumentProcessingError as exc:
        logger.exception(
            "Document processing failed: %s",
            file.filename,
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception(
            "Unexpected document analysis failure."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected document processing error.",
        ) from exc

    return serialize_pipeline_result(result)