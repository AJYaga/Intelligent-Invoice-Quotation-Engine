from dataclasses import dataclass, field
from decimal import Decimal

@dataclass
class ExtractedField:
    value: str | Decimal | None
    confidence: float
    source_text: str | None = None
    page_number: int | None = None

@dataclass
class LineItem:
    description: str
    quantity: Decimal | None
    unit_price: Decimal | None
    line_total: Decimal | None
    confidence: float

@dataclass
class ExtractionResult:
    fields: dict[str, ExtractedField] = field(default_factory=dict)
    line_items: list[LineItem] = field(default_factory=list)