from decimal import Decimal
from app.models.ocr import OCRBox, OCRLine, OCRPage, OCRResult
from app.services.extraction.fields import FieldExtractor

def line(text: str, confidence: float = 0.95) -> OCRLine:
    return OCRLine(
        text=text,
        confidence=confidence,
        box=OCRBox(
            points=[
                [0, 0],
                [100, 0],
                [100, 20],
                [0, 20],
            ]
        ),
    )

def make_result(lines: list[OCRLine]) -> OCRResult:
    return OCRResult(
        pages=[
            OCRPage(
                page_number=1,
                lines=lines,
                mean_confidence=0.95,
            )
        ],
        full_text="\n".join(item.text for item in lines),
        mean_confidence=0.95,
    )

def test_extract_document_number():
    result = FieldExtractor().extract(
        make_result([
            line("INVOICE"),
            line("Invoice No: INV-1001"),
        ])
    )

    assert result["document_number"].value == "INV-1001"

def test_extract_document_date():
    result = FieldExtractor().extract(
        make_result([
            line("Invoice Date: 2026-09-20"),
        ])
    )

    assert result["document_date"].value == "2026-09-20"

def test_extract_vendor():
    result = FieldExtractor().extract(
        make_result([
            line("Vendor: ABC Technologies"),
        ])
    )

    assert result["vendor_name"].value == "ABC Technologies"

def test_extract_financial_fields():
    result = FieldExtractor().extract(
        make_result([
            line("Subtotal: LKR 10000.00"),
            line("Discount: LKR 500.00"),
            line("VAT: LKR 1710.00"),
            line("Shipping: LKR 250.00"),
            line("Grand Total: LKR 11460.00"),
        ])
    )

    assert result["subtotal"].value == Decimal("10000.00")
    assert result["discount"].value == Decimal("500.00")
    assert result["tax"].value == Decimal("1710.00")
    assert result["additional_charges"].value == Decimal("250.00")
    assert result["grand_total"].value == Decimal("11460.00")

def test_extract_currency():
    result = FieldExtractor().extract(
        make_result([
            line("Total: LKR 10000.00"),
        ])
    )

    assert result["currency"].value == "LKR"

def test_missing_field_is_not_invented():
    result = FieldExtractor().extract(
        make_result([
            line("INVOICE"),
        ])
    )

    assert result["document_number"].value is None
    assert result["document_number"].confidence == 0.0