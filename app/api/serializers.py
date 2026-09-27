from decimal import Decimal
from app.models.response import (
    DocumentAnalysisResponse,
    FieldResponse,
    LineItemResponse,
    ValidationIssueResponse,
)
from app.pipeline.document_pipeline import PipelineResult

def serialize_value(value):
    if isinstance(value, Decimal):
        return float(value)

    return value

def serialize_pipeline_result(
    result: PipelineResult,
) -> DocumentAnalysisResponse:
    fields = {
        name: FieldResponse(
            value=serialize_value(field.value),
            confidence=field.confidence,
        )
        for name, field in result.extraction.fields.items()
    }

    line_items = [
        LineItemResponse(
            description=item.description,
            quantity=(
                float(item.quantity)
                if item.quantity is not None
                else None
            ),
            unit_price=(
                float(item.unit_price)
                if item.unit_price is not None
                else None
            ),
            line_total=(
                float(item.line_total)
                if item.line_total is not None
                else None
            ),
            confidence=item.confidence,
        )
        for item in result.extraction.line_items
    ]

    validation_issues = [
        ValidationIssueResponse(
            code=issue.code,
            message=issue.message,
            severity=issue.severity.value,
            field=issue.field,
        )
        for issue in result.validation.issues
    ]

    return DocumentAnalysisResponse(
        document_type=(
            result.classification.document_type.value
        ),
        confidence=result.validation.confidence,
        fields=fields,
        line_items=line_items,
        validation_issues=validation_issues,
        status=result.validation.status.value,
    )