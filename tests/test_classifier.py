from app.models.classification import DocumentType
from app.models.ocr import OCRResult
from app.services.classification.classifier import DocumentClassifier

def make_ocr_result(text: str) -> OCRResult:
    return OCRResult(
        pages=[],
        full_text=text,
        mean_confidence=0.95,
    )

def test_invoice_classification():
    result = DocumentClassifier().classify(
        make_ocr_result(
            """
            TAX INVOICE
            Invoice No: INV-1001
            Due Date: 2026-09-30
            Subtotal: LKR 10000
            Tax: LKR 1800
            Total: LKR 11800
            """
        )
    )

    assert result.document_type == DocumentType.INVOICE
    assert result.confidence > 0.5
    assert result.invoice_score > result.quotation_score

def test_quotation_classification():
    result = DocumentClassifier().classify(
        make_ocr_result(
            """
            QUOTATION
            Quotation No: QT-2045
            Valid Until: 2026-10-30
            Subtotal: USD 1000
            Tax: USD 100
            Total: USD 1100
            """
        )
    )

    assert result.document_type == DocumentType.QUOTATION
    assert result.confidence > 0.5
    assert result.quotation_score > result.invoice_score

def test_unknown_document():
    result = DocumentClassifier().classify(
        make_ocr_result(
            """
            Meeting Notes
            Project planning discussion
            September 2026
            """
        )
    )

    assert result.document_type == DocumentType.UNKNOWN

def test_financial_document_without_type_is_unknown():
    result = DocumentClassifier().classify(
        make_ocr_result(
            """
            Subtotal USD 1000
            Tax USD 100
            Total USD 1100
            """
        )
    )

    assert result.document_type == DocumentType.UNKNOWN

def test_conflicting_invoice_and_quotation_signals_are_unknown():
    result = DocumentClassifier().classify(
        make_ocr_result(
            """
            INVOICE
            QUOTATION
            Invoice No INV-1001
            Quotation No QT-1001
            Subtotal LKR 10000
            Total LKR 10000
            """
        )
    )

    assert result.document_type == DocumentType.UNKNOWN