from decimal import Decimal
from app.models.ocr import OCRBox, OCRLine, OCRPage, OCRResult
from app.services.extraction.line_items import LineItemExtractor

def make_line(
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
                [x + 80, y],
                [x + 80, y + 20],
                [x, y + 20],
            ]
        ),
    )

def test_extract_line_item():
    lines = [
        make_line("Description", 50, 100),
        make_line("Qty", 300, 100),
        make_line("Unit Price", 420, 100),
        make_line("Amount", 600, 100),
        make_line("Laptop", 50, 140),
        make_line("2", 300, 140),
        make_line("150000.00", 420, 140),
        make_line("300000.00", 600, 140),
        make_line("Subtotal", 420, 190),
        make_line("300000.00", 600, 190),
    ]

    ocr_result = OCRResult(
        pages=[
            OCRPage(
                page_number=1,
                lines=lines,
                mean_confidence=0.95,
            )
        ],
        full_text="\n".join(line.text for line in lines),
        mean_confidence=0.95,
    )

    items = LineItemExtractor().extract(ocr_result)

    assert len(items) == 1

    item = items[0]

    assert item.description == "Laptop"
    assert item.quantity == Decimal("2")
    assert item.unit_price == Decimal("150000.00")
    assert item.line_total == Decimal("300000.00")

def test_alternative_table_headers():
    lines = [
        make_line("Item", 50, 100),
        make_line("Quantity", 300, 100),
        make_line("Rate", 420, 100),
        make_line("Total", 600, 100),
        make_line("Consulting", 50, 140),
        make_line("3", 300, 140),
        make_line("5000", 420, 140),
        make_line("15000", 600, 140),
    ]

    ocr_result = OCRResult(
        pages=[
            OCRPage(
                page_number=1,
                lines=lines,
                mean_confidence=0.95,
            )
        ],
        full_text="\n".join(line.text for line in lines),
        mean_confidence=0.95,
    )

    items = LineItemExtractor().extract(ocr_result)

    assert len(items) == 1
    assert items[0].description == "Consulting"
    assert items[0].line_total == Decimal("15000")