import re
from datetime import datetime
from app.models.extraction import ExtractedField
from app.models.ocr import OCRLine, OCRResult
from app.services.extraction.utils import (
    empty_field,
    extract_last_amount,
    normalize_text,
)
from app.services.extraction.spatial import find_value_to_right

DOCUMENT_NUMBER_PATTERN = re.compile(
    r"\b(?:invoice|quotation|quote)\s*"
    r"(?:no\.?|number|#)\s*[:#-]?\s*"
    r"([a-z0-9][a-z0-9./_-]{1,})",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"("
    r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}"
    r"|"
    r"\d{1,2}[-/.]\d{1,2}[-/.]\d{4}"
    r"|"
    r"[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}"
    r"|"
    r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}"
    r")"
)

class FieldExtractor:
    def extract(self, ocr_result: OCRResult) -> dict[str, ExtractedField]:
        return {
            "document_number": self.extract_document_number(ocr_result),
            "document_date": self.extract_document_date(ocr_result),
            "vendor_name": self.extract_vendor(ocr_result),
            "currency": self.extract_currency(ocr_result),
            "subtotal": self.extract_subtotal(ocr_result),
            "discount": self.extract_discount(ocr_result),
            "tax": self.extract_tax(ocr_result),
            "additional_charges": self.extract_additional_charges(ocr_result),
            "grand_total": self.extract_grand_total(ocr_result),
        }

    def extract_document_number(
        self,
        ocr_result: OCRResult,
    ) -> ExtractedField:
        labels = (
            "invoice #",
            "invoice no",
            "invoice number",
            "quotation #",
            "quotation no",
            "quotation number",
            "quote #",
            "quote no",
            "quote number",
        )

        for page in ocr_result.pages:
            for line in page.lines:
                match = DOCUMENT_NUMBER_PATTERN.search(line.text)

                if match:
                    return ExtractedField(
                        value=match.group(1),
                        confidence=round(line.confidence * 0.98, 3),
                        source_text=line.text,
                        page_number=page.page_number,
                    )

                normalized = normalize_text(line.text)

                if normalized not in labels:
                    continue

                candidate = find_value_to_right(
                    line,
                    page.lines,
                )

                if candidate is None:
                    continue

                return ExtractedField(
                    value=candidate.text.strip(),
                    confidence=round(
                        min(
                            line.confidence,
                            candidate.confidence,
                        ) * 0.95,
                        3,
                    ),
                    source_text=candidate.text,
                    page_number=page.page_number,
                )

        return empty_field()

    def extract_document_date(
        self,
        ocr_result: OCRResult,
    ) -> ExtractedField:
        labels = (
            "invoice date",
            "quotation date",
            "quote date",
            "document date",
            "date",
        )

        for page in ocr_result.pages:
            for line in page.lines:
                normalized = normalize_text(line.text)

                if not any(label in normalized for label in labels):
                    continue

                # First try: date is on the same OCR line as the label
                match = DATE_PATTERN.search(line.text)

                if match:
                    raw_date = match.group(1)
                    normalized_date, certainty = self._normalize_date(raw_date)

                    return ExtractedField(
                        value=normalized_date,
                        confidence=round(line.confidence * certainty, 3),
                        source_text=line.text,
                        page_number=page.page_number,
                    )

                # Second try: date is spatially to the right of the label
                candidate = find_value_to_right(
                    line,
                    page.lines,
                )

                if candidate is None:
                    continue

                match = DATE_PATTERN.search(candidate.text)

                if not match:
                    continue

                raw_date = match.group(1)
                normalized_date, certainty = self._normalize_date(raw_date)

                return ExtractedField(
                    value=normalized_date,
                    confidence=round(
                        min(
                            line.confidence,
                            candidate.confidence,
                        ) * certainty,
                        3,
                    ),
                    source_text=candidate.text,
                    page_number=page.page_number,
                )

        return empty_field()

    def extract_vendor(
        self,
        ocr_result: OCRResult,
    ) -> ExtractedField:
        labeled = self._extract_party(
            ocr_result,
            ("vendor", "supplier", "seller", "from"),
        )

        if labeled.value is not None:
            return labeled

        excluded = (
            "invoice",
            "quotation",
            "quote",
            "date",
            "total",
            "tax",
            "subtotal",
            "bill to",
            "ship to",
        )

        if not ocr_result.pages:
            return empty_field()

        first_page = ocr_result.pages[0]

        for index, line in enumerate(first_page.lines[:8]):
            normalized = normalize_text(line.text)

            if any(word in normalized for word in excluded):
                continue

            if sum(character.isalpha() for character in line.text) < 3:
                continue

            evidence_score = 0.70

            if index <= 2:
                evidence_score += 0.10

            if any(
                token in normalized
                for token in (
                    "inc",
                    "ltd",
                    "llc",
                    "corp",
                    "company",
                    "co.",
                    "pvt",
                )
            ):
                evidence_score += 0.10

            if index + 1 < len(first_page.lines):
                next_text = first_page.lines[index + 1].text

                if any(
                    character.isdigit()
                    for character in next_text
                ):
                    evidence_score += 0.05

            evidence_score = min(
                evidence_score,
                0.95,
            )

            return ExtractedField(
                value=line.text.strip(),
                confidence=round(
                    line.confidence * evidence_score,
                    3,
                ),
                source_text=line.text,
                page_number=first_page.page_number,
            )

        return empty_field()

    def extract_currency(self, ocr_result: OCRResult) -> ExtractedField:
        codes = ("LKR", "USD", "EUR", "GBP", "AUD", "CAD", "INR")

        for page in ocr_result.pages:
            for line in page.lines:
                upper = line.text.upper()

                for code in codes:
                    if re.search(rf"\b{code}\b", upper):
                        return ExtractedField(
                            value=code,
                            confidence=round(line.confidence * 0.95, 3),
                            source_text=line.text,
                            page_number=page.page_number,
                        )

        symbols = ("$", "€", "£")

        for page in ocr_result.pages:
            for line in page.lines:
                for symbol in symbols:
                    if symbol in line.text:
                        return ExtractedField(
                            value=symbol,
                            confidence=round(line.confidence * 0.70, 3),
                            source_text=line.text,
                            page_number=page.page_number,
                        )

        return empty_field()

    def extract_subtotal(self, ocr_result: OCRResult) -> ExtractedField:
        return self._extract_money_field(
            ocr_result,
            ("subtotal", "sub total"),
        )

    def extract_discount(self, ocr_result: OCRResult) -> ExtractedField:
        return self._extract_money_field(
            ocr_result,
            ("discount",),
        )

    def extract_tax(self, ocr_result: OCRResult) -> ExtractedField:
        return self._extract_money_field(
            ocr_result,
            ("tax", "vat", "gst"),
        )

    def extract_additional_charges(self, ocr_result: OCRResult) -> ExtractedField:
        return self._extract_money_field(
            ocr_result,
            (
                "additional charges",
                "service charge",
                "shipping",
                "delivery charge",
            ),
        )

    def extract_grand_total(
        self,
        ocr_result: OCRResult,
    ) -> ExtractedField:
        preferred_labels = (
            "grand total",
            "amount due",
            "balance due",
            "total due",
        )

        result = self._extract_money_field(
            ocr_result,
            preferred_labels,
        )

        if result.value is not None:
            return result

        for page in ocr_result.pages:
            for line in page.lines:
                normalized = normalize_text(line.text)

                if normalized != "total":
                    continue

                candidate = find_value_to_right(
                    line,
                    page.lines,
                )

                if candidate is None:
                    continue

                amount = extract_last_amount(
                    candidate.text
                )

                if amount is None:
                    continue

                return ExtractedField(
                    value=amount,
                    confidence=round(
                        min(
                            line.confidence,
                            candidate.confidence,
                        ) * 0.95,
                        3,
                    ),
                    source_text=candidate.text,
                    page_number=page.page_number,
                )

        return empty_field()

    def _extract_money_field(
        self,
        ocr_result: OCRResult,
        labels: tuple[str, ...],
    ) -> ExtractedField:
        for page in ocr_result.pages:
            for line in page.lines:
                normalized = normalize_text(line.text)

                if not any(
                    label in normalized
                    for label in labels
                ):
                    continue

                amount = extract_last_amount(
                    line.text
                )

                if (
                    amount is not None
                    and "%" not in line.text
                ):
                    return ExtractedField(
                        value=amount,
                        confidence=round(
                            line.confidence * 0.95,
                            3,
                        ),
                        source_text=line.text,
                        page_number=page.page_number,
                    )

                candidate = find_value_to_right(
                    line,
                    page.lines,
                )

                if candidate is None:
                    continue

                amount = extract_last_amount(
                    candidate.text
                )

                if amount is not None:
                    return ExtractedField(
                        value=amount,
                        confidence=round(
                            min(
                                line.confidence,
                                candidate.confidence,
                            ) * 0.95,
                            3,
                        ),
                        source_text=candidate.text,
                        page_number=page.page_number,
                    )

        return empty_field()

    def _extract_party(
        self,
        ocr_result: OCRResult,
        labels: tuple[str, ...],
    ) -> ExtractedField:
        for page in ocr_result.pages:
            lines = page.lines

            for index, line in enumerate(lines):
                normalized = normalize_text(line.text)

                matched_label = next(
                    (label for label in labels if label in normalized),
                    None,
                )

                if matched_label is None:
                    continue

                value = self._value_after_label(
                    line.text,
                    matched_label,
                )

                if value:
                    return ExtractedField(
                        value=value,
                        confidence=round(line.confidence * 0.90, 3),
                        source_text=line.text,
                        page_number=page.page_number,
                    )

                if index + 1 < len(lines):
                    next_line = lines[index + 1]

                    return ExtractedField(
                        value=next_line.text.strip(),
                        confidence=round(next_line.confidence * 0.80, 3),
                        source_text=next_line.text,
                        page_number=page.page_number,
                    )

        return empty_field()

    @staticmethod
    def _value_after_label(text: str, label: str) -> str | None:
        pattern = re.compile(
            rf"{re.escape(label)}\s*[:\-]?\s*(.+)$",
            re.IGNORECASE,
        )

        match = pattern.search(text)

        if not match:
            return None

        value = match.group(1).strip()

        if normalize_text(value) == normalize_text(label):
            return None

        return value or None

    @staticmethod
    def _normalize_date(raw: str) -> tuple[str, float]:
        iso_match = re.fullmatch(
            r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})",
            raw,
        )

        if iso_match:
            year, month, day = map(int, iso_match.groups())

            try:
                value = datetime(year, month, day)
                return value.date().isoformat(), 0.98
            except ValueError:
                return raw, 0.60

        if re.search(r"[A-Za-z]", raw):
            formats = (
                "%B %d, %Y",
                "%B %d %Y",
                "%b %d, %Y",
                "%b %d %Y",
                "%d %B %Y",
                "%d %b %Y",
            )

            for date_format in formats:
                try:
                    value = datetime.strptime(raw, date_format)
                    return value.date().isoformat(), 0.95
                except ValueError:
                    continue

        numeric = re.fullmatch(
            r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})",
            raw,
        )

        if numeric:
            first, second, year = map(int, numeric.groups())

            if first > 12 and second <= 12:
                try:
                    value = datetime(year, second, first)
                    return value.date().isoformat(), 0.90
                except ValueError:
                    pass

        return raw, 0.65