from app.models.classification import ClassificationResult
from app.models.extraction import ExtractionResult
from app.models.ocr import OCRResult
from app.models.validation import (
    ValidationIssue,
    ValidationSeverity,
)

LOW_FIELD_CONFIDENCE = 0.60
LOW_OCR_CONFIDENCE = 0.70
LOW_CLASSIFICATION_CONFIDENCE = 0.60

IMPORTANT_FIELDS = (
    "document_number",
    "document_date",
    "vendor_name",
    "customer_name",
    "subtotal",
    "tax",
    "grand_total",
)

def analyze_confidence(
    ocr_result: OCRResult,
    classification: ClassificationResult,
    extraction: ExtractionResult,
) -> tuple[float, list[ValidationIssue]]:
    issues = []

    if ocr_result.mean_confidence < LOW_OCR_CONFIDENCE:
        issues.append(
            ValidationIssue(
                code="LOW_OCR_CONFIDENCE",
                message=(
                    "Document OCR confidence is below "
                    "the accepted threshold."
                ),
                severity=ValidationSeverity.WARNING,
            )
        )

    if (
        classification.confidence
        < LOW_CLASSIFICATION_CONFIDENCE
    ):
        issues.append(
            ValidationIssue(
                code="LOW_CLASSIFICATION_CONFIDENCE",
                message=(
                    "Document classification confidence "
                    "is below the accepted threshold."
                ),
                severity=ValidationSeverity.WARNING,
                field="document_type",
            )
        )

    available_confidences = [
        ocr_result.mean_confidence,
        classification.confidence,
    ]

    for name in IMPORTANT_FIELDS:
        field = extraction.fields.get(name)

        if field is None or field.value is None:
            continue

        effective_confidence = min(
            field.confidence,
            ocr_result.mean_confidence,
        )

        available_confidences.append(
            effective_confidence
        )

        if (
            effective_confidence
            < LOW_FIELD_CONFIDENCE
        ):
            issues.append(
                ValidationIssue(
                    code="LOW_CONFIDENCE_FIELD",
                    message=(
                        f"Field '{name}' has low "
                        f"confidence "
                        f"({effective_confidence:.3f})."
                    ),
                    severity=ValidationSeverity.WARNING,
                    field=name,
                )
            )

    overall_confidence = (
        sum(available_confidences)
        / len(available_confidences)
        if available_confidences
        else 0.0
    )

    return round(overall_confidence, 3), issues