from app.models.ocr import OCRBox, OCRLine, OCRPage, OCRResult
from app.services.extraction.parties import PartyExtractor

def make_line(
    text: str,
    x: float,
    y: float,
) -> OCRLine:
    return OCRLine(
        text=text,
        confidence=0.95,
        box=OCRBox(
            points=[
                [x, y],
                [x + 100, y],
                [x + 100, y + 20],
                [x, y + 20],
            ]
        ),
    )

def make_result(
    lines: list[OCRLine],
) -> OCRResult:
    return OCRResult(
        pages=[
            OCRPage(
                page_number=1,
                lines=lines,
                mean_confidence=0.95,
            )
        ],
        full_text="\n".join(
            line.text for line in lines
        ),
        mean_confidence=0.95,
    )

def test_bill_to_block():
    result = make_result([
        make_line("BILL TO", 50, 100),
        make_line("John Smith", 50, 130),
        make_line("2 Court Square", 50, 155),
        make_line("New York, NY 12210", 50, 180),
        make_line("SHIP TO", 300, 100),
    ])

    party = PartyExtractor().extract_customer(result)

    assert party.name == "John Smith"
    assert "2 Court Square" in party.address
    assert "New York" in party.address

def test_customer_block():
    result = make_result([
        make_line("CUSTOMER", 100, 100),
        make_line("ABC Holdings", 100, 130),
        make_line("12 Main Street", 100, 155),
        make_line("Colombo", 100, 180),
    ])

    party = PartyExtractor().extract_customer(result)

    assert party.name == "ABC Holdings"
    assert "12 Main Street" in party.address

def test_sold_to_block():
    result = make_result([
        make_line("SOLD TO", 80, 100),
        make_line("XYZ Pvt Ltd", 80, 130),
        make_line("No 10 Lake Road", 80, 155),
        make_line("Kandy", 80, 180),
    ])

    party = PartyExtractor().extract_customer(result)

    assert party.name == "XYZ Pvt Ltd"
    assert "Kandy" in party.address