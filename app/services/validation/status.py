from app.models.validation import (
    ProcessingStatus,
    ValidationIssue,
    ValidationSeverity,
)

def resolve_status(
    issues: list[ValidationIssue],
) -> ProcessingStatus:
    if any(
        issue.severity
        == ValidationSeverity.FATAL
        for issue in issues
    ):
        return ProcessingStatus.INVALID

    if any(
        issue.severity
        in (
            ValidationSeverity.ERROR,
            ValidationSeverity.WARNING,
        )
        for issue in issues
    ):
        return ProcessingStatus.MANUAL_REVIEW_REQUIRED

    return ProcessingStatus.PROCESSED