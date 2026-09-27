import re
from decimal import Decimal, InvalidOperation
from app.models.extraction import ExtractedField

AMOUNT_PATTERN = re.compile(
    r"[-+]?\(?\d[\d,\s]*(?:\.\d{1,2})?\)?"
)

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()

def parse_decimal(value: str) -> Decimal | None:
    cleaned = value.strip()
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    cleaned = cleaned.strip("()")
    cleaned = cleaned.replace(",", "").replace(" ", "")

    try:
        result = Decimal(cleaned)
    except InvalidOperation:
        return None

    return -result if negative else result

def extract_last_amount(text: str) -> Decimal | None:
    matches = AMOUNT_PATTERN.findall(text)

    if not matches:
        return None

    for candidate in reversed(matches):
        value = parse_decimal(candidate)

        if value is not None:
            return value

    return None

def empty_field() -> ExtractedField:
    return ExtractedField(
        value=None,
        confidence=0.0,
        source_text=None,
        page_number=None,
    )