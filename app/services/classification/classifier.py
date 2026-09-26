import re
from app.models.classification import (
    ClassificationEvidence,
    ClassificationResult,
    DocumentType,
)
from app.models.ocr import OCRResult

class DocumentClassifier:
    INVOICE_SIGNALS = {
        "invoice": 3.0,
        "invoice no": 2.5,
        "invoice number": 2.5,
        "tax invoice": 3.0,
        "amount due": 1.5,
        "balance due": 1.5,
        "payment due": 1.0,
        "due date": 1.0,
    }

    QUOTATION_SIGNALS = {
        "quotation": 3.0,
        "quotation no": 2.5,
        "quotation number": 2.5,
        "quote no": 2.0,
        "quote number": 2.0,
        "valid until": 1.5,
        "validity": 1.0,
        "estimated price": 1.0,
    }

    COMMON_BUSINESS_SIGNALS = {
        "subtotal": 0.5,
        "total": 0.5,
        "tax": 0.5,
        "quantity": 0.5,
        "unit price": 0.5,
    }

    def classify(self, ocr_result: OCRResult) -> ClassificationResult:
        text = self._normalize_text(ocr_result.full_text)

        invoice_score = 0.0
        quotation_score = 0.0
        evidence: list[ClassificationEvidence] = []

        for signal, weight in self.INVOICE_SIGNALS.items():
            if self._contains_signal(text, signal):
                invoice_score += weight
                evidence.append(
                    ClassificationEvidence(
                        signal=signal,
                        weight=weight,
                        document_type=DocumentType.INVOICE,
                    )
                )

        for signal, weight in self.QUOTATION_SIGNALS.items():
            if self._contains_signal(text, signal):
                quotation_score += weight
                evidence.append(
                    ClassificationEvidence(
                        signal=signal,
                        weight=weight,
                        document_type=DocumentType.QUOTATION,
                    )
                )

        structural_score = self._calculate_structural_score(text)

        invoice_score += structural_score
        quotation_score += structural_score

        return self._make_decision(
            invoice_score=invoice_score,
            quotation_score=quotation_score,
            evidence=evidence,
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def _contains_signal(text: str, signal: str) -> bool:
        pattern = rf"\b{re.escape(signal)}\b"
        return re.search(pattern, text) is not None

    def _calculate_structural_score(self, text: str) -> float:
        score = 0.0

        for signal, weight in self.COMMON_BUSINESS_SIGNALS.items():
            if self._contains_signal(text, signal):
                score += weight

        currency_pattern = r"\b(?:lkr|usd|eur|gbp|aud|cad)\b|[$€£]"
        if re.search(currency_pattern, text, re.IGNORECASE):
            score += 0.5

        date_pattern = r"\b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}\b"
        if re.search(date_pattern, text):
            score += 0.5

        return min(score, 2.0)

    def _make_decision(
        self,
        invoice_score: float,
        quotation_score: float,
        evidence: list[ClassificationEvidence],
    ) -> ClassificationResult:
        highest_score = max(invoice_score, quotation_score)
        difference = abs(invoice_score - quotation_score)

        if highest_score < 2.5:
            return ClassificationResult(
                document_type=DocumentType.UNKNOWN,
                confidence=0.0,
                invoice_score=invoice_score,
                quotation_score=quotation_score,
                evidence=evidence,
            )

        if difference < 1.5:
            return ClassificationResult(
                document_type=DocumentType.UNKNOWN,
                confidence=0.5,
                invoice_score=invoice_score,
                quotation_score=quotation_score,
                evidence=evidence,
            )

        document_type = (
            DocumentType.INVOICE
            if invoice_score > quotation_score
            else DocumentType.QUOTATION
        )

        confidence = min(
            0.99,
            highest_score / (highest_score + 2.0),
        )

        return ClassificationResult(
            document_type=document_type,
            confidence=round(confidence, 3),
            invoice_score=invoice_score,
            quotation_score=quotation_score,
            evidence=evidence,
        )