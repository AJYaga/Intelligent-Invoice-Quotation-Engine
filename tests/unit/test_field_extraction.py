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

def positioned_line(
    text: str,
    x: float,
    y: float,
    confidence: float = 0.95,
) -> OCRLine:
    return OCRLine(
        text=text,
        confidence=confidence,
        box=OCRBox(
            points=[
                [x, y],
                [x + 100, y],
                [x + 100, y + 20],
                [x, y + 20],
            ]
        ),
    )

def test_extract_document_number_below_label():
    result = FieldExtractor().extract(
        make_result([
            positioned_line("QUOTE #", 300, 100),
            positioned_line("2034", 300, 130),
        ])
    )

    assert result["document_number"].value == "2034"

def test_extract_date_below_label():
    result = FieldExtractor().extract(
        make_result([
            positioned_line("DATE", 500, 100),
            positioned_line("2/12/2017", 500, 130),
        ])
    )

    assert result["document_date"].value == "2/12/2017"

def test_document_title_is_not_document_number():
    result = FieldExtractor().extract(
        make_result([
            line("INVOICE"),
        ])
    )

    assert result["document_number"].value is None

def test_ocr_noisy_quote_number_label():
    result = FieldExtractor().extract(
        make_result([
            positioned_line("QUOTE 8", 300, 100),
            positioned_line("2034", 300, 130),
        ])
    )

    assert result["document_number"].value == "2034"

def test_extract_total_quote():
    result = FieldExtractor().extract(
        make_result([
            positioned_line("TOTAL QUOTE", 300, 100),
            positioned_line("615.65", 500, 100),
        ])
    )

    assert result["grand_total"].value == Decimal("615.65")

def test_noisy_quote_label_extracts_value_below():
    result = FieldExtractor().extract(
        make_result([
            positioned_line("QUOTE 8", 300, 100),
            positioned_line("2034", 300, 130),
        ])
    )

    assert result["document_number"].value == "2034"

def test_line_item_discount_not_summary_discount():
    result = FieldExtractor().extract(
        make_result([
            positioned_line(
                "New client discount",
                50,
                100,
            ),
            positioned_line(
                "(50.00)",
                400,
                100,
            ),
        ])
    )

    assert result["discount"].value is None

def test_quote_number_prefers_same_row_over_date():
    result = FieldExtractor().extract(
        make_result([
            positioned_line("DATE", 1100, 100),
            positioned_line("01-05-2014", 1260, 100),
            positioned_line("QUOTE #", 1080, 140),
            positioned_line("[123456]", 1270, 140),
        ])
    )

    assert result["document_number"].value == "[123456]"

def test_currency_not_taken_from_description_text():
    result = FieldExtractor().extract(
        make_result([
            positioned_line(
                "Labor: 5 hours at $75/hr",
                100,
                100,
            ),
            positioned_line(
                "TOTAL",
                500,
                300,
            ),
            positioned_line(
                "921.56",
                700,
                300,
            ),
        ])
    )

    assert result["currency"].value is None

def test_invoice_title_does_not_anchor_document_number():
    result = FieldExtractor().extract(
        make_result([
            positioned_line("INVOICE", 50, 50),
            positioned_line("1912 Harvest Lane", 50, 100),
            positioned_line("INVOICE #", 500, 150),
            positioned_line("US-001", 700, 150),
        ])
    )

    assert result["document_number"].value == "US-001"

def test_extract_sales_tax_amount_to_right():
    result = FieldExtractor().extract(
        make_result([
            positioned_line(
                "Sales Tax 6.25%",
                400,
                100,
            ),
            positioned_line(
                "9.06",
                700,
                100,
            ),
        ])
    )

    assert result["tax"].value == Decimal("9.06")