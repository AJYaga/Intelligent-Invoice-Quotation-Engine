from decimal import Decimal
from app.models.extraction import ExtractionResult
from app.models.validation import (
    ValidationIssue,
    ValidationSeverity,
)

TOLERANCE = Decimal("0.02")

def close_enough(
    actual: Decimal,
    expected: Decimal,
) -> bool:
    return abs(actual - expected) <= TOLERANCE

def validate_line_items(
    extraction: ExtractionResult,
) -> list[ValidationIssue]:
    issues = []

    for index, item in enumerate(
        extraction.line_items,
        start=1,
    ):
        if (
            item.quantity is None
            or item.unit_price is None
            or item.line_total is None
        ):
            continue

        expected = item.quantity * item.unit_price

        if not close_enough(
            item.line_total,
            expected,
        ):
            issues.append(
                ValidationIssue(
                    code="LINE_TOTAL_MISMATCH",
                    message=(
                        f"Line item {index}: expected "
                        f"{expected} but found "
                        f"{item.line_total}."
                    ),
                    severity=ValidationSeverity.ERROR,
                    field="line_items",
                )
            )

    return issues

def validate_subtotal(
    extraction: ExtractionResult,
) -> list[ValidationIssue]:
    issues = []

    subtotal_field = extraction.fields.get("subtotal")

    if (
        subtotal_field is None
        or subtotal_field.value is None
        or not extraction.line_items
    ):
        return issues

    totals = [
        item.line_total
        for item in extraction.line_items
        if item.line_total is not None
    ]

    if len(totals) != len(extraction.line_items):
        return issues

    expected = sum(
        totals,
        Decimal("0"),
    )

    actual = subtotal_field.value

    if not isinstance(actual, Decimal):
        return issues

    if not close_enough(actual, expected):
        issues.append(
            ValidationIssue(
                code="SUBTOTAL_MISMATCH",
                message=(
                    f"Expected subtotal {expected} "
                    f"from line items but found "
                    f"{actual}."
                ),
                severity=ValidationSeverity.ERROR,
                field="subtotal",
            )
        )

    return issues

def validate_grand_total(
    extraction: ExtractionResult,
) -> list[ValidationIssue]:
    issues = []

    fields = extraction.fields

    subtotal = _decimal_value(
        fields,
        "subtotal",
    )
    grand_total = _decimal_value(
        fields,
        "grand_total",
    )

    if subtotal is None or grand_total is None:
        return issues

    discount = (
        _decimal_value(fields, "discount")
        or Decimal("0")
    )

    tax = (
        _decimal_value(fields, "tax")
        or Decimal("0")
    )

    charges = (
        _decimal_value(
            fields,
            "additional_charges",
        )
        or Decimal("0")
    )

    expected = (
        subtotal
        - discount
        + tax
        + charges
    )

    if not close_enough(
        grand_total,
        expected,
    ):
        issues.append(
            ValidationIssue(
                code="GRAND_TOTAL_MISMATCH",
                message=(
                    f"Expected grand total "
                    f"{expected} but found "
                    f"{grand_total}."
                ),
                severity=ValidationSeverity.ERROR,
                field="grand_total",
            )
        )

    return issues

def _decimal_value(
    fields: dict,
    name: str,
) -> Decimal | None:
    field = fields.get(name)

    if field is None:
        return None

    value = field.value

    return (
        value
        if isinstance(value, Decimal)
        else None
    )