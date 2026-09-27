from decimal import Decimal
from app.models.classification import (
    ClassificationResult,
    DocumentType,
)
from app.models.extraction import (
    ExtractedField,
    ExtractionResult,
    LineItem,
)
from app.models.ocr import OCRResult
from app.models.validation import ProcessingStatus
from app.services.validation.service import ValidationService

def make_classification(
    confidence: float = 0.95,
) -> ClassificationResult:
    return ClassificationResult(
        document_type=DocumentType.INVOICE,
        confidence=confidence,
        invoice_score=6.0,
        quotation_score=1.0,
        evidence=[],
    )

def make_extraction() -> ExtractionResult:
    return ExtractionResult(
        fields={
            "document_number": ExtractedField(
                "INV-001",
                0.95,
            ),
            "document_date": ExtractedField(
                "2026-09-20",
                0.95,
            ),
            "vendor_name": ExtractedField(
                "ABC Ltd",
                0.95,
            ),
            "customer_name": ExtractedField(
                "XYZ Ltd",
                0.95,
            ),
            "subtotal": ExtractedField(
                Decimal("145.00"),
                0.95,
            ),
            "discount": ExtractedField(
                None,
                0.0,
            ),
            "tax": ExtractedField(
                Decimal("9.06"),
                0.95,
            ),
            "additional_charges": ExtractedField(
                None,
                0.0,
            ),
            "grand_total": ExtractedField(
                Decimal("154.06"),
                0.95,
            ),
        },
        line_items=[
            LineItem(
                "Item A",
                Decimal("1"),
                Decimal("100"),
                Decimal("100"),
                0.95,
            ),
            LineItem(
                "Item B",
                Decimal("3"),
                Decimal("15"),
                Decimal("45"),
                0.95,
            ),
        ],
    )

def make_ocr(
    confidence: float = 0.95,
) -> OCRResult:
    return OCRResult(
        pages=[],
        full_text="INVOICE",
        mean_confidence=confidence,
    )

def test_valid_document_is_processed():
    result = ValidationService().validate(
        make_ocr(),
        make_classification(),
        make_extraction(),
    )

    assert result.status == ProcessingStatus.PROCESSED
    assert result.issues == []

def test_missing_document_number_requires_review():
    extraction = make_extraction()

    extraction.fields["document_number"] = (
        ExtractedField(None, 0.0)
    )

    result = ValidationService().validate(
        make_ocr(),
        make_classification(),
        extraction,
    )

    codes = [
        issue.code
        for issue in result.issues
    ]

    assert "MISSING_DOCUMENT_NUMBER" in codes
    assert (
        result.status
        == ProcessingStatus.MANUAL_REVIEW_REQUIRED
    )

def test_line_total_mismatch_detected():
    extraction = make_extraction()

    extraction.line_items[0].line_total = (
        Decimal("90")
    )

    result = ValidationService().validate(
        make_ocr(),
        make_classification(),
        extraction,
    )

    codes = [
        issue.code
        for issue in result.issues
    ]

    assert "LINE_TOTAL_MISMATCH" in codes

def test_subtotal_mismatch_detected():
    extraction = make_extraction()

    extraction.fields["subtotal"].value = (
        Decimal("150")
    )

    result = ValidationService().validate(
        make_ocr(),
        make_classification(),
        extraction,
    )

    codes = [
        issue.code
        for issue in result.issues
    ]

    assert "SUBTOTAL_MISMATCH" in codes

def test_grand_total_mismatch_detected():
    extraction = make_extraction()

    extraction.fields["grand_total"].value = (
        Decimal("200")
    )

    result = ValidationService().validate(
        make_ocr(),
        make_classification(),
        extraction,
    )

    codes = [
        issue.code
        for issue in result.issues
    ]

    assert "GRAND_TOTAL_MISMATCH" in codes

def test_low_ocr_confidence_requires_review():
    result = ValidationService().validate(
        make_ocr(0.40),
        make_classification(),
        make_extraction(),
    )

    codes = [
        issue.code
        for issue in result.issues
    ]

    assert "LOW_OCR_CONFIDENCE" in codes
    assert (
        result.status
        == ProcessingStatus.MANUAL_REVIEW_REQUIRED
    )