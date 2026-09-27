from dataclasses import dataclass
from app.models.ocr import OCRLine, OCRResult
from app.services.extraction.spatial import (
    bottom,
    center_x,
    left,
    right,
    top,
)
from app.services.extraction.utils import normalize_text

@dataclass
class PartyBlock:
    name: str | None
    address: str | None
    confidence: float

class PartyExtractor:
    CUSTOMER_LABELS = (
        "bill to",
        "customer",
        "client",
        "sold to",
        "buyer",
    )

    SHIPPING_LABELS = (
        "ship to",
        "deliver to",
        "shipping address",
    )

    VENDOR_LABELS = (
        "vendor",
        "supplier",
        "seller",
        "from",
    )

    STOP_LABELS = (
        "invoice",
        "invoice #",
        "invoice no",
        "invoice number",
        "quotation",
        "quotation #",
        "quotation no",
        "date",
        "invoice date",
        "quotation date",
        "due date",
        "subtotal",
        "total",
        "grand total",
        "tax",
        "vat",
        "description",
        "qty",
        "quantity",
        "unit price",
        "amount",
        "ship to",
        "bill to",
    )

    def extract_customer(
        self,
        ocr_result: OCRResult,
    ) -> PartyBlock:
        return self._extract_labeled_block(
            ocr_result,
            self.CUSTOMER_LABELS,
        )

    def _extract_labeled_block(
        self,
        ocr_result: OCRResult,
        labels: tuple[str, ...],
    ) -> PartyBlock:
        for page in ocr_result.pages:
            for line in page.lines:
                normalized = normalize_text(line.text)

                if normalized not in labels:
                    continue

                candidates = self._find_block_lines(
                    anchor=line,
                    lines=page.lines,
                )

                if not candidates:
                    continue

                name = candidates[0].text.strip()

                address_lines = [
                    candidate.text.strip()
                    for candidate in candidates[1:]
                ]

                address = (
                    ", ".join(address_lines)
                    if address_lines
                    else None
                )

                confidence = sum(
                    candidate.confidence
                    for candidate in candidates
                ) / len(candidates)

                return PartyBlock(
                    name=name,
                    address=address,
                    confidence=round(confidence, 3),
                )

        return PartyBlock(
            name=None,
            address=None,
            confidence=0.0,
        )

    def _find_block_lines(
        self,
        anchor: OCRLine,
        lines: list[OCRLine],
    ) -> list[OCRLine]:
        anchor_center_x = center_x(anchor)
        anchor_width = right(anchor) - left(anchor)

        candidates = []

        for line in lines:
            if line is anchor:
                continue

            if top(line) < bottom(anchor):
                continue

            vertical_distance = top(line) - bottom(anchor)

            if vertical_distance > 120:
                continue

            horizontal_distance = abs(
                center_x(line) - anchor_center_x
            )

            allowed_horizontal_distance = max(
                120.0,
                anchor_width * 2.5,
            )

            if horizontal_distance > allowed_horizontal_distance:
                continue

            normalized = normalize_text(line.text)

            if normalized in self.STOP_LABELS:
                continue

            candidates.append(line)

        candidates.sort(
            key=lambda item: top(item)
        )

        return candidates[:4]