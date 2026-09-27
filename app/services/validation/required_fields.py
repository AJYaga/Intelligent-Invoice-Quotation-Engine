from app.models.extraction import ExtractionResult
from app.models.validation import (
    ValidationIssue,
    ValidationSeverity,
)

REQUIRED_FIELDS = (
    "document_number",
    "document_date",
    "grand_total",
)

def validate_required_fields(
    extraction: ExtractionResult,
) -> list[ValidationIssue]:
    issues = []

    for field_name in REQUIRED_FIELDS:
        field = extraction.fields.get(field_name)

        if field is None or field.value is None:
            issues.append(
                ValidationIssue(
                    code=f"MISSING_{field_name.upper()}",
                    message=f"Required field '{field_name}' is missing.",
                    severity=ValidationSeverity.ERROR,
                    field=field_name,
                )
            )

    return issues