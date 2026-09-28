import re
from decimal import Decimal, InvalidOperation
from app.models.extraction import ExtractedField
from difflib import SequenceMatcher

AMOUNT_PATTERN = re.compile(
    r"[-+]?\(?\d[\d,\s]*(?:\.\d{1,2})?\)?"
)

DATE_LIKE_PATTERN = re.compile(
    r"\b("
    r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}"
    r"|"
    r"\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}"
    r")\b"
)

def looks_like_date(text: str) -> bool:
    return DATE_LIKE_PATTERN.search(text.strip()) is not None

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()

def parse_decimal(value: str) -> Decimal | None:
    cleaned = value.strip()

    if not cleaned:
        return None

    negative = (
        cleaned.startswith("(")
        and cleaned.endswith(")")
    )

    cleaned = cleaned.strip("()")

    cleaned = re.sub(
        r"[^\d.,+\-]",
        "",
        cleaned,
    )

    cleaned = cleaned.replace(",", "")

    if cleaned in {
        "",
        "+",
        "-",
        ".",
    }:
        return None

    try:
        result = Decimal(cleaned)
    except InvalidOperation:
        return None

    if negative:
        result = -result

    return result

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

def semantic_label_match(
    text: str,
    labels: tuple[str, ...],
    threshold: float = 0.80,
) -> bool:
    normalized_text = re.sub(
        r"[^a-z0-9]",
        "",
        normalize_text(text),
    )

    for label in labels:
        normalized_label = re.sub(
            r"[^a-z0-9]",
            "",
            normalize_text(label),
        )

        similarity = SequenceMatcher(
            None,
            normalized_text,
            normalized_label,
        ).ratio()

        if similarity >= threshold:
            return True

    return False