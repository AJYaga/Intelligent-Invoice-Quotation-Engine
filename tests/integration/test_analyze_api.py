from decimal import Decimal
from fastapi.testclient import TestClient
from app.api.dependencies import get_document_pipeline
from app.main import app
from app.models.classification import (
    ClassificationResult,
    DocumentType,
)
from app.models.extraction import (
    ExtractedField,
    ExtractionResult,
)
from app.models.ocr import OCRResult
from app.models.validation import (
    ProcessingStatus,
    ValidationResult,
)
from app.pipeline.document_pipeline import PipelineResult

class FakePipeline:
    def analyze(
        self,
        file_bytes: bytes,
        filename: str,
    ) -> PipelineResult:
        return PipelineResult(
            ocr=OCRResult(
                pages=[],
                full_text="INVOICE",
                mean_confidence=0.95,
            ),
            classification=ClassificationResult(
                document_type=DocumentType.INVOICE,
                confidence=0.95,
                invoice_score=6.0,
                quotation_score=1.0,
                evidence=[],
            ),
            extraction=ExtractionResult(
                fields={
                    "document_number": ExtractedField(
                        value="INV-1001",
                        confidence=0.96,
                    ),
                    "grand_total": ExtractedField(
                        value=Decimal("154.06"),
                        confidence=0.95,
                    ),
                },
                line_items=[],
            ),
            validation=ValidationResult(
                issues=[],
                status=ProcessingStatus.PROCESSED,
                confidence=0.94,
            ),
        )

def override_pipeline():
    return FakePipeline()

app.dependency_overrides[
    get_document_pipeline
] = override_pipeline

client = TestClient(app)

def test_analyze_document():
    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "invoice.png",
                b"valid-placeholder-content",
                "image/png",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_type"] == "INVOICE"
    assert data["status"] == "PROCESSED"
    assert data["fields"]["document_number"]["value"] == "INV-1001"
    assert data["fields"]["grand_total"]["value"] == 154.06

def test_analyze_rejects_unsupported_file():
    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "notes.txt",
                b"hello",
                "text/plain",
            )
        },
    )

    assert response.status_code == 415

def test_analyze_rejects_empty_file():
    response = client.post(
        "/api/documents/analyze",
        files={
            "file": (
                "invoice.pdf",
                b"",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400